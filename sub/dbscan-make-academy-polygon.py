# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 01:04:31 2021

@author: user
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, MultiPoint
from shapely.geometry import MultiPolygon, JOIN_STYLE
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

epsg4326 = from_string("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs") # from_string은 좌표 지정할 때 쓰는 코드
epsg5174 = from_string("+proj=tmerc +lat_0=38 +lon_0=127.0028902777778 +k=1 +x_0=200000 +y_0=500000 +ellps=bessel +units=m +no_defs +towgs84=-115.80,474.99,674.11,1.16,-2.31,-1.63,6.43")
#epsg5179 = from_string("+proj=tmerc +lat_0=38 +lon_0=127.5 +k=0.9996 +x_0=1000000 +y_0=2000000 +ellps=GRS80 +units=m +no_defs")
#epsg5181 = from_string("+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=500000 +ellps=GRS80 +units=m +no_defs")
epsg5181_qgis = from_string("+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=500000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs") # qgis 좌표, 보정좌표값 존재
#epsg5186 = from_string("+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=600000 +ellps=GRS80 +units=m +no_defs")
epsg2097 = from_string("+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=500000 +ellps=bessel +units=m +no_defs +towgs84=-115.80,474.99,674.11,1.16,-2.31,-1.63,6.43")
cc=CRS({'init':'epsg:4326', 'no_defs':True})


# 학원 point를 찍고 DBSCAN을 통해 군집을 시킨 다음에 학군지도 만들어보기

academy=pd.read_csv(r'D:\부동산 빅데이터 분석 스터디\아파트 찾기 프로젝트 수정\소상공인시장진흥공단_상가(상권)정보_서울_202012.csv', encoding='utf-8', sep='|')
academy=academy.loc[academy['상권업종대분류명']=='학문/교육']
academy=academy.loc[(academy['상권업종중분류명']=='학원-보습교습입시') | (academy['상권업종소분류명']=='운동/코치학교')| (academy['상권업종중분류명']=='학원-컴퓨터') | (academy['상권업종중분류명']=='학원-음악미술미용') | (academy['상권업종중분류명']=='학원-예능취미체육') | (academy['상권업종중분류명']=='학원-어학')]

academy['geometry']=academy.apply(lambda row : Point(row['경도'], row['위도']), axis=1)
academy=gpd.GeoDataFrame(academy, geometry='geometry', crs=cc)
academy=academy.to_crs(epsg5181_qgis)

academy['x_meter']=''
academy['y_meter']=''

for i in academy.index :
    academy.loc[i, 'x_meter']=academy.loc[i, 'geometry'].coords.xy[0][0]
    academy.loc[i, 'y_meter']=academy.loc[i, 'geometry'].coords.xy[1][0]
    
dbscan_df=academy[['x_meter', 'y_meter']]
dbscan_df=dbscan_df.rename(columns={'x_meter' : 'x', 'y_meter' : 'y'})

dbscan=DBSCAN(min_samples=5, eps=200) 
clusters=dbscan.fit_predict(dbscan_df) # -1은 잡음(군집되지 않은 점)

# print(f'category : {clusters}')

# plt.scatter(dbscan_df['x'],dbscan_df['y'], c=clusters, marker='o',s=10)

academy['category']=clusters

academy2=academy[['상호명', '상권업종중분류명', '상권업종소분류명', '표준산업분류명', '시군구코드', '시군구명', '행정동코드', '행정동명', '법정동코드', '법정동명', '지번코드', '지번본번지', '지번부번지', '지번주소', '도로명코드', '도로명', '건물본번지', '건물부번지', '건물관리번호', '건물명', '도로명주소', '경도', '위도', 'x_meter', 'y_meter', 'geometry' , 'category']]

academy_noise=academy2[academy2['category']==-1]

academy_dbscan=academy2[academy2['category']!=-1]

#%%
# lat = academy_dbscan['위도'].mean()
# long = academy_dbscan['경도'].mean()

# m = folium.Map([lat,long],zoom_start=10)

# for i in academy_dbscan.index:
#     sub_lat =  academy_dbscan.loc[i,'위도']
#     sub_long = academy_dbscan.loc[i,'경도']
    
#     title = academy_dbscan.loc[i,'상호명']
  
#     color = 'blue'
    
#     iframe=folium.IFrame(academy_dbscan.loc[i,'상호명'], width=450, height=60)
#     popup=folium.Popup(iframe)
#     folium.Marker([sub_lat,sub_long], popup=popup, icon=folium.Icon(icon='home', color=color)).add_to(m)

# m.save('danji_apt_academy_2.html')

#%%
# 상권 폴리곤 만들기

def cal_len(df) :
    df2=df.drop_duplicates(subset='geometry')
    df_len=len(df2)
    return df_len

def convexhull(df, count) :
    df_empty=df[df['geometry']==1]
    df_merge=df.dissolve(by='category')
    df_merge['category']=count
    
    convex=df_merge.convex_hull.geometry[count]
    df_merge['geometry']=convex
    
    return df_merge

category_max=np.max(academy_dbscan['category'])
academy_category=academy_dbscan.copy()
academy_empty=academy_category[academy_category['geometry']==1]

for i in tqdm(range(category_max+1)) :
    academy_category=academy_dbscan[academy_dbscan['category']==i]
    aca_len=cal_len(academy_category)
    if aca_len > 2 :
        academy_empty=academy_empty.append(convexhull(academy_category, i))

# print(academy_empty.crs)
academy_empty=academy_empty.to_crs(epsg=4326)

lat = academy_empty['위도'].mean()
long = academy_empty['경도'].mean()

m = folium.Map([lat,long],zoom_start=10, title='academy')

for _, r in academy_empty.iterrows():
    
    # simplify를 쓰나 안쓰나 차이는 별로 없으나 geopandas 원문에서 쓰라고 하니 써주자
    
    sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j,
                           style_function = lambda x: {'fillColor': 'blue'})
    # folium.Popup(r['법정동명']).add_to(geo_j)
    geo_j.add_to(m)

m.save('danji_apt_academy_convex_2.html')
