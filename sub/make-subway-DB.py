# -*- coding: utf-8 -*-
"""
Created on Wed May 12 01:17:08 2021

@author: user
"""

import re
from selenium import webdriver
import seaborn as sns
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, MultiPoint
from shapely.geometry import MultiPolygon
import itertools
from fiona.crs import from_string
from pyproj import CRS
import openpyxl
import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
from sklearn.cluster import DBSCAN
from sklearn import datasets
import matplotlib.pyplot as plt
%matplotlib inline 
from sklearn.cluster import KMeans 
from scipy.spatial.distance import cdist
import warnings
warnings.filterwarnings(action='ignore') 
import folium
import os

os.getcwd()
os.chdir('D:/부동산 빅데이터 분석 스터디/아파트 찾기 프로젝트 수정')

epsg5178 = from_string('+proj=tmerc +lat_0=38 +lon_0=127.5 +k=0.9996 +x_0=1000000 +y_0=2000000 +ellps=bessel +units=m +no_defs +towgs84=-115.80,474.99,674.11,1.16,-2.31,-1.63,6.43')
epsg4326 = from_string("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs") # from_string은 좌표 지정할 때 쓰는 코드
epsg5174 = from_string("+proj=tmerc +lat_0=38 +lon_0=127.0028902777778 +k=1 +x_0=200000 +y_0=500000 +ellps=bessel +units=m +no_defs +towgs84=-115.80,474.99,674.11,1.16,-2.31,-1.63,6.43")
#epsg5179 = from_string("+proj=tmerc +lat_0=38 +lon_0=127.5 +k=0.9996 +x_0=1000000 +y_0=2000000 +ellps=GRS80 +units=m +no_defs")
#epsg5181 = from_string("+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=500000 +ellps=GRS80 +units=m +no_defs")
epsg5181_qgis = from_string("+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=500000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs") # qgis 좌표, 보정좌표값 존재
#epsg5186 = from_string("+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=600000 +ellps=GRS80 +units=m +no_defs")
epsg2097 = from_string("+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=500000 +ellps=bessel +units=m +no_defs +towgs84=-115.80,474.99,674.11,1.16,-2.31,-1.63,6.43")

cc=CRS({'init':'epsg:4326', 'no_defs':True})



#%%

# 지하철 이름, 좌표가 담긴 shp 입력

subway=gpd.GeoDataFrame.from_file(r'D:\부동산 빅데이터 분석 스터디\아파트 찾기 프로젝트 수정\전자지도_배경DB_20210412\TL_SPSB_STATN.shp', encoding='cp949', geometry='geometry')
subway.crs=epsg5178
print(subway.crs)

subway=subway.to_crs(epsg5181_qgis)

subway['시도코드']=subway['SIG_CD'].str[:2]
subway=subway[subway['시도코드']=='11']

for i in subway.index :
    sep=subway.loc[i, 'KOR_SUB_NM'].split('(')[0]
    if '역' in sep :
        subway.loc[i, '역 이름']=sep
    else :
        subway.loc[i, '역 이름']=sep+'역'

subway['역 이름']=subway['역 이름'].str[:-1]

# 서울시 지하철호선별 역별 승하차 인원 정보 csv를 통해서 호선명 추출

subway_ho=pd.read_csv(r'D:\부동산 빅데이터 분석 스터디\아파트 찾기 프로젝트 수정\서울시 지하철호선별 역별 승하차 인원 정보.csv', encoding='cp949')
subway_ho['사용일자'] = pd.to_datetime(subway_ho['사용일자'], format='%Y%m%d')

subway_ho=subway_ho.set_index('사용일자')
subway_ho=subway_ho.loc['2021-05-08', :]

subway_ho=subway_ho[['호선명', '역명']]
subway_ho.reset_index(inplace=True)

for i in subway_ho.index :
    for j in subway.index :
        if (subway_ho.loc[i, '역명'] in subway.loc[j, '역 이름']) | (subway.loc[j, '역 이름'] in subway_ho.loc[i, '역명']) :
            if subway.loc[j, 'geometry'].geom_type!='MultiPolygon' :
                subway_ho.loc[i, 'geometry']=subway.loc[j, 'geometry']
            else :
                subway_ho.loc[i, 'geometry']=subway.loc[[j], 'geometry'].values

subway_ho_geo=gpd.GeoDataFrame(subway_ho, geometry='geometry', crs=epsg5181_qgis)

subway_ho_geo=subway_ho_geo.dropna(subset=['geometry'])

del subway_ho_geo['사용일자']

# 호선명 수정

for i in subway_ho_geo.index :
    if (subway_ho_geo.loc[i, '호선명']=='경부선') | (subway_ho_geo.loc[i, '호선명']=='경인선'):
        subway_ho_geo.loc[i, '호선명']='1호선'
        
    if (subway_ho_geo.loc[i, '호선명']=='경의선') | (subway_ho_geo.loc[i, '호선명']=='중앙선') | (subway_ho_geo.loc[i, '호선명']=='경원선'):
        subway_ho_geo.loc[i, '호선명']='경의중앙선'
        
    if subway_ho_geo.loc[i, '호선명']=='공항철도 1호선' :
        subway_ho_geo.loc[i, '호선명']='공항철도'
        
    if subway_ho_geo.loc[i, '호선명']=='9호선2~3단계' :
        subway_ho_geo.loc[i, '호선명']='9호선'

# 환승역 유무 따지기

for i in subway_ho_geo.index :
    transfer_count=0
    for j in subway_ho_geo.index :
        if subway_ho_geo.loc[i, '역명']==subway_ho_geo.loc[j, '역명'] :
            transfer_count+=1
    
    if transfer_count>1 :
        subway_ho_geo.loc[i, '환승역유무']='o'
    else :
        subway_ho_geo.loc[i, '환승역유무']='x'

# 저장
subway_ho_geo.to_file(r'D:\부동산 빅데이터 분석 스터디\아파트 찾기 프로젝트 수정\subway.shp', encoding='cp949')


