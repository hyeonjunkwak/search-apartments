# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 13:36:52 2021

@author: user
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Apr  3 02:28:21 2021

@author: user
"""

import re
from selenium import webdriver
import seaborn as sns
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

os.getcwd()
os.chdir('D:/부동산 빅데이터 분석 스터디/아파트 찾기 프로젝트 수정')

epsg4326 = from_string("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs") # from_string은 좌표 지정할 때 쓰는 코드
epsg5174 = from_string("+proj=tmerc +lat_0=38 +lon_0=127.0028902777778 +k=1 +x_0=200000 +y_0=500000 +ellps=bessel +units=m +no_defs +towgs84=-115.80,474.99,674.11,1.16,-2.31,-1.63,6.43")
#epsg5179 = from_string("+proj=tmerc +lat_0=38 +lon_0=127.5 +k=0.9996 +x_0=1000000 +y_0=2000000 +ellps=GRS80 +units=m +no_defs")
#epsg5181 = from_string("+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=500000 +ellps=GRS80 +units=m +no_defs")
epsg5181_qgis = from_string("+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=500000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs") # qgis 좌표, 보정좌표값 존재
#epsg5186 = from_string("+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=600000 +ellps=GRS80 +units=m +no_defs")
epsg2097 = from_string("+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=500000 +ellps=bessel +units=m +no_defs +towgs84=-115.80,474.99,674.11,1.16,-2.31,-1.63,6.43")
cc=CRS({'init':'epsg:4326', 'no_defs':True})

#%%

# 사용해야할 필터 리스트 - 세대수, 경과연수, 종합병원거리, 초등학교거리, 중학교거리, 고등학교거리, 도시공원거리, 지하철 호선 및 거리, 대규모점포 유무

print('\n\n본 프로그램은 입력하신 조건에 부합하는 아파트를 출력해주는 프로그램입니다.')
time.sleep(4)
print('지금부터 사용법에 대해서 설명해드리겠습니다.')
time.sleep(3)
print()
print('먼저 사용하실 수 있는 필터 리스트는 아래와 같습니다.')
time.sleep(3)
print()
print('[세대수, 경과연수, 종합병원거리, 초등학교거리, 중학교거리, 고등학교거리, 공원거리, 지하철 호선 및 거리, 대규모점포거리]')
time.sleep(5)
print()
print('이제 입력 방법에 대해서 설명드리겠습니다.\n')
time.sleep(4)
print('세대수 조건은 특정 세대수 이상의 아파트를 찾고 싶으실 때 사용하는 조건입니다. 사용법은 세대수700 이렇게 띄어쓰기 없이 적어주시면 됩니다.\n')
time.sleep(7)
print('경과연수 조건은 특정 경과연도 이하의 아파트를 찾고 싶으실 때 사용하는 조건입니다. 사용법은 경과연수15 이렇게 띄어쓰기 없이 적어주시면 됩니다.\n')
time.sleep(7)
print('종합병원거리, 초등학교거리, 중학교거리, 고등학교거리, 공원거리 조건은 특정 거리 이내에 종합병원, 초등학교, 중학교, 고등학교, 공원이 있는 아파트를 찾고 싶으실 때 사용하는 조건입니다.\n사용법은 종합병원500 중학교700 이렇게 미터단위로 적어주시면 됩니다.\n')
time.sleep(8)
print('지하철 호선 및 거리 조건은 특정 호선 주위 및 역으로부터 특정 거리 이내의 아파트를 찾을 때 사용하는 조건입니다.\n사용법은 3호선500 이렇게 호선과 거리를 m단위로 띄어쓰기 없이 적어주시면 됩니다. 참고로 거리를 700m로 설정하시길 권장드립니다.\n')
time.sleep(8)
print('마지막 대규모 점포거리 조건입니다. 특정 거리 이내에 대규모점포가 있는 아파트를 검색할 때 사용하는 조건입니다. 사용법은 대규모점포거리700 이렇게 적어주시면 됩니다\n')
time.sleep(7)
s=input('자, 이제 조건을 쭉 나열해주시면 됩니다. 예시처럼 조건들을 입력해주세요. 순서는 상관없습니다.\n\n예시 :세대수700 경과연수10 종합병원거리500 초등학교거리400 중학교거리600 고등학교거리800 공원거리400 3호선500 대규모점포거리500\n').split(' ')
work_place=input('직장 위치를 입력해주세요. 되도록이면 주변에 위치한 점포명을 입력해주시길 바랍니다. ex) 서울역 스타벅스\n')
value=input('입력하신 조건 중 가장 중요시하는 조건 하나를 선택해주세요. 선택하신 조건순으로 정렬해서 결과를 출력하겠습니다.\n[세대수, 경과연수, 종합병원거리, 초등학교거리, 중학교거리, 고등학교거리, 공원거리, 지하철] 중에 하나만 입력해주세요(대규모점포거리 순으로 정렬은 안되는 점 양해부탁드립니다)\n')
pyung=input('마지막입니다. 관심있으신 아파트의 평수범위를 선택해주세요 (A,B,C로 입력해주세요!)\n선택지 -> A. 20평이상~29평이하,       B. 30평이상~39평이하       C. 40평이상~49평이하\n')

#%%

# 서울 아파트 csv 불러오기

danji_apt=pd.read_csv(r'D:\부동산 빅데이터 분석 스터디\아파트 찾기 프로젝트 수정\서울 아파트.csv', encoding='cp949', sep=',')
del danji_apt['Unnamed: 0']
del danji_apt['geometry']
danji_apt_sexy=danji_apt.copy() # 실거래가 조회할때 쓰기 위함
danji_apt.rename(columns={'사용연수' : '경과연수', 'k-전체세대수' : '세대수', 'k-아파트명' : '건물 이름'}, inplace=True)
danji_apt=danji_apt[(danji_apt['세대수']>=200) | danji_apt['건물 이름'].str.contains('자이|힐스테이트|래미안|푸르지오|e편한세상|센트럴 아이파크|센트럴아이파크|롯데캐슬')] # 적어도 200세대 이상인 아파트(단지형 아파트 파일인데 은근 나홀로 아파트가 많음), 대충 2700개정도 날라감

danji_apt['geometry'] = danji_apt.apply(lambda row: Point(row.좌표X, row.좌표Y), axis=1)

danji_apt_geo=gpd.GeoDataFrame(danji_apt, geometry='geometry', crs=cc)

danji_apt_geo=danji_apt_geo.to_crs(epsg5181_qgis)

danji_apt_geo=danji_apt_geo.dropna(subset=['건물 이름']) 

#%%

# 먼저 생활하면서 필수적인 편의점 유무부터 거르고 가자. 

sangga_upso=pd.read_csv(r'D:\부동산 빅데이터 분석 스터디\아파트 찾기 프로젝트 수정\소상공인시장진흥공단_상가(상권)정보_서울_202012.csv', encoding='utf-8', sep='|')
sangga_upso=sangga_upso.loc[sangga_upso['상권업종소분류명'].str.contains('편의점')]
sangga_upso=sangga_upso.loc[sangga_upso['상호명'].str.contains('씨유|CU|Cu|cu|지에스|GS25|Gs25|gs25|GS|Gs|gs|세븐일레븐|코리아세븐|위드미|비지에프리테일|미니스톱|훼미리|비지에프|Emart|emart|이마트')]
sangga_upso=sangga_upso.rename(columns={'경도' : 'x', '위도' : 'y'})
sangga_upso['level'] = pd.qcut(sangga_upso.x, 10, labels=False)
sangga_upso['geometry']=sangga_upso.apply(lambda row : Point(row.x, row.y), axis=1)
cc3=CRS({'init':'epsg:4326', 'no_defs':True})
sangga_upso_geo=gpd.GeoDataFrame(sangga_upso, geometry='geometry', crs=cc3)
sangga_upso_geo=sangga_upso_geo.to_crs(epsg5181_qgis)

a=danji_apt_geo[danji_apt_geo['건물 이름']=='1']

for i in tqdm(range(10), desc="편의점 작업중...") :
    sangga_upso_geo1=sangga_upso_geo.loc[sangga_upso_geo['level']==i]

    sangga_upso_geo_buffer1=gpd.GeoDataFrame(sangga_upso_geo1.buffer(500))
    sangga_upso_geo_buffer1.columns=['geometry']
    sangga_upso_geo_buffer1=gpd.GeoDataFrame(sangga_upso_geo_buffer1, geometry='geometry')
    sangga_upso_geo_buffer1['new_column'] = 0
    sangga_upso_geo_buffer1_merge = sangga_upso_geo_buffer1.dissolve(by='new_column')

    danji_apt_convi=danji_apt_geo.loc[danji_apt_geo.geometry.within(sangga_upso_geo_buffer1_merge.geometry.unary_union)] # unary_union multipolygon의 합집합을 반환.
    
    a=pd.concat([a, danji_apt_convi]) 

b=a.drop_duplicates(subset='geometry') # 500m 이내에 편의점에 전혀 없는 아파트 26개가 걸러짐

danji_apt_geo=b

#%%

# 해당 아파트로부터 반경 450m 이내에 아파트 세대수 합계가 1500세대 이상인 아파트만 추출. 

# for문으로 각 아파트 buffer(450)를 그리고 그 원안에 속하는 아파트만 세대수 더하기.
count_ori=len(danji_apt_geo)

danji_apt_geo_sedae=danji_apt_geo.copy()
danji_apt_geo_sedae=danji_apt_geo_sedae.drop_duplicates('건물 이름')

count=len(danji_apt_geo_sedae)

danji_apt_geo_sedae=danji_apt_geo_sedae.reset_index()
del danji_apt_geo_sedae['index']

danji_apt_geo_sedae['450m 반경 내 아파트 세대수(해당 아파트 포함)']=''

for i in tqdm(range(count), desc='450m 반경 내 아파트 세대수 세는중...') :
    buf=danji_apt_geo_sedae.loc[i, 'geometry'].buffer(450)
    danji_apt_inter=danji_apt_geo_sedae.loc[danji_apt_geo_sedae.geometry.intersects(buf)]
    sedae_sum=np.sum(danji_apt_inter['세대수'])
    danji_apt_geo_sedae.loc[i, '450m 반경 내 아파트 세대수(해당 아파트 포함)']=sedae_sum # buf에 intersects하면 해당 아파트 자신은 무조건 포함되므로 따로 더할 필요 x

# 1000세대 이상으로 하면 200개, 1500세대 이상은 350개, 2000세대 이상은 500개 아파트 걸러짐    
danji_apt_geo_sedae=danji_apt_geo_sedae[danji_apt_geo_sedae['450m 반경 내 아파트 세대수(해당 아파트 포함)']>=1500]

danji_apt_geo=pd.merge(danji_apt_geo, danji_apt_geo_sedae[['건물 이름', '450m 반경 내 아파트 세대수(해당 아파트 포함)']], on='건물 이름', how='inner')

danji_apt_machine=danji_apt_geo.copy() # 맨 아래에서 kmeans에 쓸 데이터프레임 만들기

#%%

# 조건의 필터 역할을 할 함수들을 정의

def year_filter(p) :
    danji_apt_year=danji_apt_geo.loc[danji_apt_geo['경과연수']<p]
    return danji_apt_year

def sedae_filter(p1) :
    danji_apt_saedae=danji_apt_geo.loc[danji_apt_geo['세대수']>p1]
    return danji_apt_saedae

def park_filter(p2) :
    danji_apt_park=danji_apt_geo.loc[danji_apt_geo['주요 공원 거리']<p2]
    return danji_apt_park
                                                                             
def elementary_filter(p3) :
    danji_apt_elementary=danji_apt_geo.loc[danji_apt_geo['초등학교거리']<p3]
    return danji_apt_elementary

def e(p4) :
    danji_apt_middleschool=danji_apt_geo.loc[danji_apt_geo['중학교거리']<p4]
    return danji_apt_middleschool

def f(p9) :
    danji_apt_highschool=danji_apt_geo.loc[danji_apt_geo['고등학교거리']<p9]
    return danji_apt_highschool

def g(p5, p6) :
    global subway2, danji_apt_copy, subway_location, mini1
    subway=gpd.GeoDataFrame.from_file(r'D:\부동산 빅데이터 분석 스터디\아파트 찾기 프로젝트 수정\subway.shp', encoding='cp949')
    subway=subway[subway['호선명']==p5]
    subway2=subway.to_crs(epsg5181_qgis)
    
    # buffer를 이용해서 지하철 역으로부터 특정 반경 이내 아파트 조회  
    subway3=gpd.GeoDataFrame(subway2, geometry=subway2.buffer(p6).geometry)
    danji_apt_copy=danji_apt_copy.reset_index()
    subway3=subway3.reset_index()
    del danji_apt_copy['index']
    del subway3['index']
    danji_apt_copy['주변 지하철 역']=''
    danji_apt_copy['환승역 유무']=0
    
    subway_location={'geometry' : []}
    
    for i in range(len(danji_apt_copy)) :
        super_list=[]
        transfer_count=0
        for j in range(len(subway3)) :
            if danji_apt_copy.iloc[i].geometry.within(subway3.iloc[j].geometry) :
                subway_location['geometry'].append(subway3.iloc[j].geometry)
                ola=subway3['호선명'][j]+' '+ subway3['역명'][j]+'역'
                super_list.append(ola)
                danji_apt_copy['주변 지하철 역'][i]=super_list
                if subway3.iloc[j]['환승역유무']=='o' :
                    transfer_count+=1
                
        danji_apt_copy['환승역 유무'][i]=transfer_count
        if danji_apt_copy['환승역 유무'][i]>0 :
            danji_apt_copy['환승역 유무'][i]='O'
        else :
            danji_apt_copy['환승역 유무'][i]='X'
        
    danji_apt_copy=danji_apt_copy.loc[danji_apt_copy['주변 지하철 역']!='']
    mini1=gpd.GeoDataFrame(subway_location, geometry='geometry')
    return danji_apt_copy

def h(p7):
    danji_apt_hospital=danji_apt_geo.loc[danji_apt_geo['종합병원거리']<p7]
    return danji_apt_hospital

# 대규모 점포필터

def huge(p8):
    global huge_sangga_geo2, danji_apt_copy, mini2
    huge_sangga=pd.read_csv(r'D:\부동산 빅데이터 분석 스터디\아파트 찾기 프로젝트 수정\서울특별시 대규모점포 인허가 정보.csv', sep=',', encoding='cp949')
    huge_sangga=huge_sangga.rename(columns={'좌표정보(X)' : 'x', '좌표정보(Y)' : 'y'})
    huge_sangga=huge_sangga.loc[huge_sangga['x'].notnull()]
    huge_sangga=huge_sangga.loc[huge_sangga['y'].notnull()]
    huge_sangga['geometry']=huge_sangga.apply(lambda row : Point(row.x, row.y), axis=1)

    cc2=CRS({'init':'epsg:2097', 'no_defs':True})

    huge_sangga_geo=gpd.GeoDataFrame(huge_sangga, geometry='geometry', crs=cc2)
    huge_sangga_geo1=huge_sangga_geo.to_crs(epsg5181_qgis)

    huge_sangga_geo2=gpd.GeoDataFrame(huge_sangga_geo1, geometry=huge_sangga_geo1.buffer(p8).geometry)
    danji_apt_copy=danji_apt_copy.reset_index()
    huge_sangga_geo2=huge_sangga_geo2.reset_index()
    del huge_sangga_geo2['index']
    danji_apt_copy['주변 대규모 상가 이름']=''
    danji_apt_copy['주변 대규모 상가 개수']=0
    huge_sangga_location={'geometry' : []}
    
    for i in range(len(danji_apt_copy)) :
        super_list=[]
        huge_sangga_count=0
        for j in range(len(huge_sangga_geo2)) :
            if danji_apt_copy.iloc[i].geometry.within(huge_sangga_geo2.iloc[j].geometry) :
                huge_sangga_location['geometry'].append(huge_sangga_geo2.iloc[j].geometry)
                super_list.append(huge_sangga_geo2['사업장명'][j])
                huge_sangga_count+=1
                
        danji_apt_copy['주변 대규모 상가 이름'][i]=super_list
        danji_apt_copy['주변 대규모 상가 개수'][i]=huge_sangga_count
               
    danji_apt_copy=danji_apt_copy.loc[danji_apt_copy['주변 대규모 상가 개수']!=0]
    mini2=gpd.GeoDataFrame(huge_sangga_location, geometry='geometry')
    return danji_apt_copy

#%%
huge_check=0
subway_check=0

p8=0 # 대규모점포 조건이 있는지 판단하기 위한 변수
p5=0
academy=0 # 초, 중, 고 거리가 있으면 +1씩 더해서 0보다 클 경우에는 학원 polygon과 쪼인
namelists='' # 조건 이름이 들어가게 될 변수

for i in tqdm(s, desc="조건 필터링중..."): # for문으로 입력받은 조건을 돌림
 
    if '경과연수' in i:
        p=i[4:]
        p=int(p)
        danji_apt_geo=year_filter(p)
        danji_apt_copy=danji_apt_geo.copy()
        namelists=namelists+str(i)+', '
        
    if '세대수' in i :
        p1=i[3:]
        p1=int(p1)
        danji_apt_geo=sedae_filter(p1)
        danji_apt_copy=danji_apt_geo.copy()
        namelists=namelists+str(i)+', '
        
    if '공원거리' in i :
        p2=i[4:]
        p2=int(p2)
        danji_apt_geo=park_filter(p2)
        danji_apt_copy=danji_apt_geo.copy()
        namelists=namelists+str(i)+', '
        
    if '초등학교거리' in i :
        p3=i[6:]
        p3=int(p3)
        danji_apt_geo=elementary_filter(p3)
        danji_apt_copy=danji_apt_geo.copy()
        namelists=namelists+str(i)+', '
        academy+=1
        
    if '중학교거리' in i :
        p4=i[5:]
        p4=int(p4)
        danji_apt_geo=e(p4)
        danji_apt_copy=danji_apt_geo.copy()
        namelists=namelists+str(i)+', '
        academy+=1

    if ('호선' in i) or ('우이신설' in i) or ('경의중앙선' in i) or ('공항철도' in i) or ('경춘선' in i) or ('신분당선' in i) or ('분당선' in i) : 
        p6=700
        
        if '호선' in i :
            p5=i[:3]
            if len(i)>3 :
                p6=i[3:]
                p6=int(p6)
                
        elif '우이신설' in i :
            p5=i[:4]
            if len(i)>4 :
                p6=i[4:]
                p6=int(p6)
                
        elif '경의중앙선' in i :
            p5=i[:5]
            if len(i)>5 :
                p6=i[5:]
                p6=int(p6)
        
        elif '공항철도' in i :
            p5=i[:4]
            if len(i)>4 :
                p6=i[4:]
                p6=int(p6)
                
        elif '경춘선' in i :
            p5=i[:3]
            if len(i)>3 :
                p6=i[3:]
                p6=int(p6)
                
        elif '신분당선' in i :
            p5=i[:4]
            if len(i)>4 :
                p6=i[4:]
                p6=int(p6)
        
        elif '분당선' in i :
            p5=i[:3]
            if len(i)>3 :
                p6=i[3:]
                p6=int(p6)
        
        danji_apt_copy=danji_apt_geo.copy()
        danji_apt_geo=g(p5, p6)
        danji_apt_copy=danji_apt_geo.copy()
        namelists=namelists+str(i)+', '
        subway_check+=1
        
    if '종합병원거리' in i :
        p7=i[6:]
        p7=int(p7)
        danji_apt_geo=h(p7)
        danji_apt_copy=danji_apt_geo.copy()
        namelists=namelists+str(i)+', '
        
    if '대규모점포거리' in i :
        p8=i[7:]
        p8=int(p8)
        danji_apt_copy=danji_apt_geo.copy()
        danji_apt_geo=huge(p8)
        del danji_apt_geo['index']
        danji_apt_copy=danji_apt_geo.copy()
        namelists=namelists+str(i)+', '
        huge_check+=1
        
    if '고등학교거리' in i :
        p9=i[6:] 
        p9=int(p9)
        danji_apt_geo=f(p9)
        danji_apt_copy=danji_apt_geo.copy()
        namelists=namelists+str(i)+', '
        academy+=1

if academy>0 :
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
    
    for i in tqdm(range(category_max+1), desc='학원 지도 만드는중...') :
        academy_category=academy_dbscan[academy_dbscan['category']==i]
        aca_len=cal_len(academy_category)
        if aca_len > 2 :
            academy_empty=academy_empty.append(convexhull(academy_category, i))
    
    danji_apt_geo['academy']=''
        
    academy_empty['a']=1
    academy_empty2=academy_empty.dissolve(by='a')
    
    for i in tqdm(danji_apt_geo.index, desc='700m 이내에 학원이 있는 아파트 추출중...') : # 700m가 도보 10분거리
        if danji_apt_geo.loc[i, 'geometry'].buffer(700).intersects(academy_empty2.geometry.unary_union)==True : 
           danji_apt_geo.loc[i, 'academy']=1
        else :
            danji_apt_geo.loc[i, 'academy']=0
    
    danji_apt_geo=danji_apt_geo.loc[danji_apt_geo['academy']==1] # 700m 이내에 학원이 있는 아파트
    del danji_apt_geo['academy']

print('\n\n조건 필터링 끝!\n')

namelists=namelists+ '직장위치_' + work_place + ', ' + '정렬조건_ '+ value + ', ' + '관심 평수_ ' 
if pyung=='A' :
    namelists = namelists + '30평 이하'
elif pyung =='B' :
    namelists = namelists + '30평 이상 ~ 39평 이하'
else :
    namelists = namelists + '40평 이상'
    
#%%

# 마지막 아파트 중복제거
danji_apt_geo_final=danji_apt_geo.drop_duplicates(subset='geometry')
danji_apt_geo_final=danji_apt_geo_final.loc[danji_apt_geo_final['건물 이름'].notnull()]
danji_apt_geo_final=danji_apt_geo_final.loc[danji_apt_geo_final['경과연수']>=0]

# 가장 중요한 조건으로 입력받은 조건을 기준으로 오름차순 또는 내림차순
if value=='세대수' : 
    danji_apt_geo_final=danji_apt_geo_final.sort_values('세대수', ascending=False)
if value=='경과연수' :
    danji_apt_geo_final=danji_apt_geo_final.sort_values('경과연수')
if value=='종합병원거리' :
    danji_apt_geo_final=danji_apt_geo_final.sort_values('종합병원거리')
if value=='초등학교거리' :
    danji_apt_geo_final=danji_apt_geo_final.sort_values('초등학교거리')
if value=='중학교거리' :
    danji_apt_geo_final=danji_apt_geo_final.sort_values('중학교거리')
if value=='고등학교거리' :
    danji_apt_geo_final=danji_apt_geo_final.sort_values('고등학교거리')
if value=='도시공원거리' :
    danji_apt_geo_final=danji_apt_geo_final.sort_values('주요 공원 거리')
if value=='지하철' :
    danji_apt_geo_final=danji_apt_geo_final.sort_values('지하철거리')

# 법정동 컬럼 만들기

danji_apt_geo_final['법정동']=''

for i in danji_apt_geo_final.index :
    danji_apt_geo_final.loc[i, '법정동']=danji_apt_geo_final.loc[i, '주소(읍면동)']

#%%

# 직장과의 거리 구글 api로 받아오기 # 새벽에하면 새벽 기준으로 길찾기를 하기 때문에 정확한 시간이 안나옴
def find_places(searching) :
    url= "https://dapi.kakao.com/v2/local/search/keyword.json?query={}".format(searching)
    headers={"Authorization": "KakaoAK 1f26ccd78d132c1a8df33f46e92cabce"}
    places=requests.get(url,headers=headers).json()['documents'] # json 형식으로 받아
    place=places[0]
    name=place['place_name']
    x=place['x']
    y=place['y']
    data=[name, x, y, searching]
    return data

try :
    final=find_places(work_place) # 직장과 가까운 점포명.. 예를들면 역곡역 스타벅스
    print(final)
    work_x=final[1] # 경도 저장
    work_y=final[2] # 위도 저장

except :
    work_place=input('검색에 실패하였습니다. 카카오맵에서 검색 가능한 점포명을 입력해주세요!\n')
    final=find_places(work_place) # 직장과 가까운 점포명.. 예를들면 역곡역 스타벅스
    print(final)
    work_x=final[1] # 경도 저장
    work_y=final[2] # 위도 저장

danji_apt_geo_final['직장 통근시간']=''
final_count=len(danji_apt_geo_final)
danji_apt_geo_final=danji_apt_geo_final.reset_index()
del danji_apt_geo_final['index']

time.sleep(1)

for i in tqdm(range(final_count), desc='직장 통근시간 계산중...') :
    x=danji_apt_geo_final.loc[i, '좌표X']
    y=danji_apt_geo_final.loc[i, '좌표Y']
    key=''
    url=f'https://maps.googleapis.com/maps/api/directions/json?origin={y},{x}&destination={work_y},{work_x}&mode=transit&departure_time=now&language=ko&key={key}'
    res=requests.get(url)
    json_dict=res.json()

    route=json_dict["routes"][0]["legs"][0]
    route_second=route["duration"]["value"]
    route_minute_second=str(route_second//60)+'분 '+str(route_second%60)+'초'
    danji_apt_geo_final.loc[i, '직장 통근시간']=route_minute_second
    
#%%
# danji_apt_geo_final.columns
# '주소(시도)k-apt주소split', '주소(시군구)', '주소(읍면동)', '건물 이름', 'k-전체동수', '세대수', '경과연수', '초등학교거리', '중학교거리', '고등학교거리', '종합병원거리', '주요 공원 거리', '450m 반경 내 아파트 세대수(해당 아파트 포함)', '직장 통근시간', 'k-복도유형', 'k-난방방식','k-전용면적별세대현황(60㎡이하)', 'k-전용면적별세대현황(60㎡~85㎡이하)', 'k-85㎡~135㎡이하', 'k-135㎡초과', '주차대수', '좌표X', '좌표Y', 'geometry'

# 대규모 점포 조건과 지하철 조건이 있는지 따져보기
if (p8!=0) & (p5!=0):
    danji_apt_geo_final2=danji_apt_geo_final[['주소(시도)k-apt주소split', '주소(시군구)', '주소(읍면동)', '건물 이름', 'k-전체동수', '세대수', '경과연수', '지하철거리', '주변 지하철 역', '환승역 유무','초등학교거리', '중학교거리', '고등학교거리', '종합병원거리', '주요 공원 거리', '주변 대규모 상가 이름', '주변 대규모 상가 개수','450m 반경 내 아파트 세대수(해당 아파트 포함)', '직장 통근시간', 'k-복도유형', 'k-난방방식','k-전용면적별세대현황(60㎡이하)', 'k-전용면적별세대현황(60㎡~85㎡이하)', 'k-85㎡~135㎡이하', 'k-135㎡초과',  '좌표X', '좌표Y', 'geometry']]

elif (p8!=0) & (p5==0) :
    danji_apt_geo_final2=danji_apt_geo_final[['주소(시도)k-apt주소split', '주소(시군구)', '주소(읍면동)', '건물 이름', 'k-전체동수', '세대수', '경과연수', '지하철거리','초등학교거리', '중학교거리', '고등학교거리', '종합병원거리', '주요 공원 거리', '주변 대규모 상가 이름', '주변 대규모 상가 개수','450m 반경 내 아파트 세대수(해당 아파트 포함)', '직장 통근시간', 'k-복도유형', 'k-난방방식','k-전용면적별세대현황(60㎡이하)', 'k-전용면적별세대현황(60㎡~85㎡이하)', 'k-85㎡~135㎡이하', 'k-135㎡초과',  '좌표X', '좌표Y', 'geometry']]

elif (p8==0) & (p5!=0):
    danji_apt_geo_final2=danji_apt_geo_final[['주소(시도)k-apt주소split', '주소(시군구)', '주소(읍면동)', '건물 이름', 'k-전체동수', '세대수', '경과연수', '지하철거리', '주변 지하철 역', '환승역 유무','초등학교거리', '중학교거리', '고등학교거리', '종합병원거리', '주요 공원 거리', '450m 반경 내 아파트 세대수(해당 아파트 포함)', '직장 통근시간', 'k-복도유형', 'k-난방방식','k-전용면적별세대현황(60㎡이하)', 'k-전용면적별세대현황(60㎡~85㎡이하)', 'k-85㎡~135㎡이하', 'k-135㎡초과',  '좌표X', '좌표Y', 'geometry']]

else :
    danji_apt_geo_final2=danji_apt_geo_final[['주소(시도)k-apt주소split', '주소(시군구)', '주소(읍면동)', '건물 이름', 'k-전체동수', '세대수', '경과연수', '지하철거리', '초등학교거리', '중학교거리', '고등학교거리', '종합병원거리', '주요 공원 거리','450m 반경 내 아파트 세대수(해당 아파트 포함)', '직장 통근시간', 'k-복도유형', 'k-난방방식','k-전용면적별세대현황(60㎡이하)', 'k-전용면적별세대현황(60㎡~85㎡이하)', 'k-85㎡~135㎡이하', 'k-135㎡초과', '좌표X', '좌표Y', 'geometry']]

#%%

# pnu 만들기

for i in danji_apt_geo_final2.index :
    sep=danji_apt_geo_final2.loc[i, '건물 이름'].split('(')[0]
    danji_apt_geo_final2.loc[i, '건물 이름']=sep
    

def find_xy(searching) :
    url= "https://dapi.kakao.com/v2/local/search/keyword.json?query={}".format(searching)
    headers={"Authorization": "KakaoAK 1f26ccd78d132c1a8df33f46e92cabce"}
    places=requests.get(url,headers=headers).json()['documents']
    
    try :
        place=places[0]        
        jibeon=place['address_name'].split(' ')[3]
        
    except :
        jibeon=np.nan
        
    return jibeon

empty=[]

for i in danji_apt_geo_final2.index :
    empty.append(find_xy(danji_apt_geo_final2.loc[i,'건물 이름']))

jibeon_df=pd.DataFrame(empty)
danji_apt_geo_final2.insert(loc=3,column='Jibeon',value=jibeon_df)

#%%
for_pnu=pd.read_csv(r'D:\부동산 빅데이터 분석 스터디\상권 프로젝트 수정\상권 프로젝트\상권 프로젝트\소상공인시장진흥공단_상가(상권)정보_서울.csv', engine='python', encoding='utf-8', sep='|')
for_pnu=for_pnu.drop_duplicates(subset='법정동코드')

bjdcode_list=[]

for i in danji_apt_geo_final2.index :
    for j in for_pnu.index :
        if danji_apt_geo_final2.loc[i, '주소(읍면동)'] == for_pnu.loc[j, '법정동명'] :
            bjdcode_list.append(str(for_pnu.loc[j, '법정동코드']))
bjd_df=pd.DataFrame(bjdcode_list)
danji_apt_geo_final2.insert(loc=3, column='법정동코드', value=bjd_df)

for i in danji_apt_geo_final2.index :
    if '-' in danji_apt_geo_final2.loc[i, 'Jibeon'] :
        danji_apt_geo_final2.loc[i, 'bonbeon']=danji_apt_geo_final2.loc[i, 'Jibeon'].split('-')[0].zfill(4)
        danji_apt_geo_final2.loc[i, 'boobeon']=danji_apt_geo_final2.loc[i, 'Jibeon'].split('-')[1].zfill(4)
    else :
        danji_apt_geo_final2.loc[i, 'bonbeon']=danji_apt_geo_final2.loc[i, 'Jibeon'].zfill(4)
        danji_apt_geo_final2.loc[i, 'boobeon']='0000'
    
    danji_apt_geo_final2.loc[i, 'PNU']=danji_apt_geo_final2.loc[i, '법정동코드']+'1'+danji_apt_geo_final2.loc[i, 'bonbeon']+danji_apt_geo_final2.loc[i, 'boobeon']

danji_apt_geo_final2.to_csv(r'D:\부동산 빅데이터 분석 스터디\아파트 찾기 프로젝트 수정\중간 저장.csv', encoding='cp949')

#%%

# 보라매 sk view 아파트가 실거래가 xml에서는 보라매에스케이뷰 아파트로 나옴. 지번주소코드로 한번 더 조인시켜야할듯
# 지번 안에 '-'가 있는지 판단하고 그게 있으면 '-'의 index를 반환. 그리고 '-'앞까지만 본번, 그 뒤는 부번으로 저장.
# sexy_poor는 pnu와 주소로 법정동 이름을 추출하는 dataframe. xml은 법정동코드가 없기에 이 dataframe과 xml의 법정동과 쪼인해서 xml에 법정동코드 부여.

sexy_poor2=for_pnu.copy()
poor_count=len(sexy_poor2)
danji_apt_geo_final2['법정동 구 코드']=danji_apt_geo_final2['법정동코드'].str[:5]

# 국토교통부 아파트 실거래가 Api를 이용해서 실거래가 컬럼 추가하기

empty_moong={'가장 최근 실거래가' : [], '거래 금액' : []}
dict_sig={}

for moong1, moong2, moong3 in zip(danji_apt_geo_final2['법정동 구 코드'], danji_apt_geo_final2['건물 이름'], danji_apt_geo_final2['PNU']):
    print(f'{moong2} 실거래가 받아오는중...')
    month_list=['202103', '202102', '202101', '202012', '202011', '202010', '202009', '202008', '202007', '202006', '202005', '202004', '202003']
    a=pd.DataFrame(columns=['Year', 'Month','Day','Apart','Floor','Area','Price', 'Dong', 'Bonbeon', 'Boobeon', 'Dongcode'])
    apart_name=moong2
    apart_name2=apart_name[:].replace(" ", "")
    sexy_count2=0 # 월별로 해당 아파트의 거래가 있는지 체크하기 위한 변수
    sig_number=moong1
    
    for m in month_list :
        if moong1 not in dict_sig.keys() :
            dict_sig[moong1]={}
            servicekey=''
            url='http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade?LAWD_CD={}&DEAL_YMD={}&serviceKey={}'.format(moong1, m, servicekey)
            res=requests.get(url)
            na_me=m
            dict_sig[sig_number][na_me]={}
            dict_sig[sig_number][na_me]=BeautifulSoup(res.content, 'xml')
            soup=BeautifulSoup(res.content, 'xml')
        
        else :
            if m in dict_sig[moong1].keys() :
                na_me=m
                soup=dict_sig[moong1][na_me]
            else : 
                servicekey=''
                url='http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade?LAWD_CD={}&DEAL_YMD={}&serviceKey={}'.format(moong1, m, servicekey)
                res=requests.get(url)
                na_me=m
                dict_sig[sig_number][na_me]={}
                dict_sig[sig_number][na_me]=BeautifulSoup(res.content, 'xml')
                soup=BeautifulSoup(res.content, 'xml')
        
       
       
        finding=soup.find_all('item')
        my_dict = {"Year":[],"Month":[],"Day":[],"Apart":[],"Floor":[],"Area":[],"Price":[], "Dong" : [], "Bonbeon" : [], "Boobeon" : [], "Dongcode" : []}

        # finding을 for문 돌려서 출력되는 아파트, 층, 전용면적, 거래금액을 dictionary의 value로 추가하기.
    
        for i in finding :
            year=i.find('년').text.strip()
            
            month=i.find('월').text.strip()

            day=i.find('일').text.strip()

            apart=i.find('아파트').text.strip()

            floor=i.find('층').text.strip()

            area=i.find('전용면적').text.strip()

            price=i.find('거래금액').text.strip()
            
            dong=i.find('법정동').text.strip()
            try : # 지번이 없는게 있음
                jibeon=i.find('지번').text.strip()
            except :
                jibeon='0000'
            
            if '-' in jibeon :
                bonbeon=jibeon[:jibeon.index('-')].zfill(4)
                boobeon=jibeon[jibeon.index('-')+1:].zfill(4)
            else :
                bonbeon=jibeon.zfill(4)
                boobeon='0000'
                
            for i in sexy_poor2.index :
                if dong==sexy_poor2.loc[i, '법정동명']:
                    dongcode=str(sexy_poor2.loc[i, '법정동코드'])[5:] # xml에서는 법정동코드가 없기 때문에 법정동명과 법정동코드가 있는 파일과 매칭해서 법정동 코드를 가져옴
                    break
                
                else :
                    dongcode='00000'
                    
            my_dict["Year"].append(year)
            my_dict["Month"].append(month)
            my_dict["Day"].append(day)
            my_dict["Apart"].append(apart)
            my_dict["Floor"].append(floor)
            my_dict["Area"].append(area)
            my_dict["Price"].append(price)
            my_dict["Dong"].append(dong)
            my_dict["Bonbeon"].append(bonbeon)
            my_dict["Boobeon"].append(boobeon)
            my_dict["Dongcode"].append(dongcode)


        apart_data=pd.DataFrame.from_dict(my_dict)
        
        apart_data['PNU']=moong1+apart_data['Dongcode']+'1'+apart_data['Bonbeon']+apart_data['Boobeon']
        
        apart_data['PNU']= apart_data['PNU'].astype(str)
        
        apart_name3=apart_name2.replace('e', '이')
        
        apart_name4=apart_name3.split('아파트')[0]
        
        b=apart_data.loc[(apart_data['Apart'].str.contains(apart_name)) | apart_data['Apart'].str.contains(apart_name2) | apart_data['PNU'].str.contains(moong3) | apart_data['Apart'].str.contains(apart_name3) | apart_data['Apart'].str.contains(apart_name4)]
        b['Area']=b['Area'].astype(float)

        if pyung=='A' : # 29평 이하 선택시에 실행
            c=b.loc[(b['Area']<=76) & (b['Area']>58)]

        elif pyung=='B' : # 30평 이상 39평 이하 선택시에 실행
            c=b.loc[(b['Area']>76) & (b['Area']<103)]
            
        else : # 40평 이상 선택시에 실행
            c=b.loc[(b['Area']>=103) & (b['Area']<125)]
        
        sexy_count1=c['Apart'].count() # 조건에 부합하는 아파트가 있는지 확인하기 위함
        if sexy_count1>0 :
            sexy_count2+=1 # 조건에 부합하는 아파트가 있다면 월별 카운트를 +1
            d=c.drop_duplicates('Month', keep='last')
            a=pd.concat([d,a])
            break
        
    if sexy_count2>0 : 
        price_final=a.drop_duplicates(subset='Apart', keep='first')
        price_final['Area']=price_final['Area'].astype(str)
        if len(price_final)>1 :
            price_final=price_final.iloc[[0]]
        
        price_length= len(price_final['Price'].values[0])
        
        if price_length==7 :
            front=price_final['Price'].values[0][:2]
            behind=price_final['Price'].values[0][2:]
            
        elif price_length==6 :
            front=price_final['Price'].values[0][:1]
            behind=price_final['Price'].values[0][1:]
    
        empty=''
        empty2=''
        
        for index, row in price_final.iterrows() :
            empty=empty+row['Year']+'년 '+row['Month']+'월 '+row['Day']+'일 / '+row['Apart']+' '+row['Floor']+ '층 / 전용면적 : ' + row['Area']+ ' m2'
            empty2= front + '억 ' + behind + '만원'
                
        empty_moong['가장 최근 실거래가'].append(empty)
        empty_moong['거래 금액'].append(empty2)
    
    else : # 2020.03부터 한번이라도 거래된적이 없음
        empty_moong['가장 최근 실거래가'].append(f'{moong2} / 1년간 거래 없음')
        empty_moong['거래 금액'].append('')
        
#%%
# 딕셔너리로 입력받은 값을 DataFrame으로 바꿔준 후 컬럼 추가
print('\n\n모든 작업 끝!')

empty_moong_data=pd.DataFrame.from_dict(empty_moong)

danji_apt_geo_final2=danji_apt_geo_final2.reset_index() # concat 하기 위해서 index를 초기화
danji_apt_geo_final3=pd.concat([danji_apt_geo_final2, empty_moong_data],axis=1) # concat을 이용해서 index 번호로 가로로 병합
del danji_apt_geo_final3['index']

if (p8!=0) & (p5!=0):
    danji_apt_geo_final3=danji_apt_geo_final3[['PNU', '주소(시군구)', '주소(읍면동)', '건물 이름', 'k-전체동수', '세대수', '경과연수', '지하철거리', '주변 지하철 역', '환승역 유무','초등학교거리', '중학교거리', '고등학교거리', '종합병원거리', '주요 공원 거리', '주변 대규모 상가 이름', '주변 대규모 상가 개수','450m 반경 내 아파트 세대수(해당 아파트 포함)', '직장 통근시간', '가장 최근 실거래가', '거래 금액', 'k-복도유형', 'k-난방방식','k-전용면적별세대현황(60㎡이하)', 'k-전용면적별세대현황(60㎡~85㎡이하)', 'k-85㎡~135㎡이하', 'k-135㎡초과', '좌표X', '좌표Y', 'geometry']]

elif (p8!=0) & (p5==0) :
    danji_apt_geo_final3=danji_apt_geo_final3[['PNU', '주소(시군구)', '주소(읍면동)', '건물 이름', 'k-전체동수', '세대수', '경과연수', '지하철거리', '초등학교거리', '중학교거리', '고등학교거리', '종합병원거리', '주요 공원 거리', '주변 대규모 상가 이름', '주변 대규모 상가 개수','450m 반경 내 아파트 세대수(해당 아파트 포함)', '직장 통근시간', '가장 최근 실거래가', '거래 금액', 'k-복도유형', 'k-난방방식','k-전용면적별세대현황(60㎡이하)', 'k-전용면적별세대현황(60㎡~85㎡이하)', 'k-85㎡~135㎡이하', 'k-135㎡초과', '좌표X', '좌표Y', 'geometry']]

elif (p8==0) & (p5!=0):
    danji_apt_geo_final3=danji_apt_geo_final3[['PNU', '주소(시군구)', '주소(읍면동)', '건물 이름', 'k-전체동수', '세대수', '경과연수', '지하철거리', '주변 지하철 역', '환승역 유무','초등학교거리', '중학교거리', '고등학교거리', '종합병원거리', '주요 공원 거리', '450m 반경 내 아파트 세대수(해당 아파트 포함)', '직장 통근시간', '가장 최근 실거래가', '거래 금액', 'k-복도유형', 'k-난방방식','k-전용면적별세대현황(60㎡이하)', 'k-전용면적별세대현황(60㎡~85㎡이하)', 'k-85㎡~135㎡이하', 'k-135㎡초과', '좌표X', '좌표Y', 'geometry']]

else :
    danji_apt_geo_final3=danji_apt_geo_final3[['PNU', '주소(시군구)', '주소(읍면동)', '건물 이름', 'k-전체동수', '세대수', '경과연수', '지하철거리', '초등학교거리', '중학교거리', '고등학교거리', '종합병원거리', '주요 공원 거리','450m 반경 내 아파트 세대수(해당 아파트 포함)', '직장 통근시간', '가장 최근 실거래가', '거래 금액', 'k-복도유형', 'k-난방방식','k-전용면적별세대현황(60㎡이하)', 'k-전용면적별세대현황(60㎡~85㎡이하)', 'k-85㎡~135㎡이하', 'k-135㎡초과', '좌표X', '좌표Y', 'geometry']]

danji_apt_geo_final3=danji_apt_geo_final3.dropna(axis=1, how='all')

#%%
answer=input('너무 많은 아파트가 검색되었나요? (번호를 입력해주세요!) 1. 네 , 너무 많습니다  2. 아니요, 딱 좋습니다!\n')

if answer=='1' :
    danji_apt_geo=danji_apt_geo_final3.copy()
    danji_apt_copy=danji_apt_geo_final3.copy()

cir=0

while (answer=='1') | (answer=='3') :
    
    save_df=danji_apt_geo.copy()
    
    print(f'\n기존에 입력된 조건은 다음과 같습니다 : {s}\n')
    
    print('입력 가능한 조건 리스트 : [세대수, 경과연수, 종합병원거리, 초등학교거리, 중학교거리, 고등학교거리, 공원거리, 지하철 호선 및 거리, 대규모점포거리]\n')

    condition=input('변경하실 조건이나 추가하실 조건을 처음과 동일한 방법으로 입력해주세요!\n').split(' ')
    namelists2='' # 조건 이름이 들어가게 될 변수
    
    for i in tqdm(condition, desc="조건 필터링중..."): # for문으로 입력받은 조건을 돌림
     
        if '경과연수' in i:
            p=i[4:]
            p=int(p)
            danji_apt_geo=year_filter(p)
            danji_apt_copy=danji_apt_geo.copy()
            namelists2=namelists2+str(i)+', '
            
        if '세대수' in i :
            p1=i[3:]
            p1=int(p1)
            danji_apt_geo=sedae_filter(p1)
            danji_apt_copy=danji_apt_geo.copy()
            namelists2=namelists2+str(i)+', '
            
        if '공원거리' in i :
            p2=i[4:]
            p2=int(p2)
            danji_apt_geo=park_filter(p2)
            danji_apt_copy=danji_apt_geo.copy()
            namelists2=namelists2+str(i)+', '
            
        if '초등학교거리' in i :
            p3=i[6:]
            p3=int(p3)
            danji_apt_geo=elementary_filter(p3)
            danji_apt_copy=danji_apt_geo.copy()
            namelists2=namelists2+str(i)+', '
            
        if '중학교거리' in i :
            p4=i[5:]
            p4=int(p4)
            danji_apt_geo=e(p4)
            danji_apt_copy=danji_apt_geo.copy()
            namelists2=namelists2+str(i)+', '
    
        if ('호선' in i) or ('우이신설' in i) or ('경의중앙선' in i) or ('공항철도' in i) or ('경춘선' in i) or ('신분당선' in i) or ('분당선' in i) : 
            p6=700
            
            if '호선' in i :
                p5=i[:3]
                if len(i)>3 :
                    p6=i[3:]
                    p6=int(p6)
                    
            elif '우이신설' in i :
                p5=i[:4]
                if len(i)>4 :
                    p6=i[4:]
                    p6=int(p6)
                    
            elif '경의중앙선' in i :
                p5=i[:5]
                if len(i)>5 :
                    p6=i[5:]
                    p6=int(p6)
            
            elif '공항철도' in i :
                p5=i[:4]
                if len(i)>4 :
                    p6=i[4:]
                    p6=int(p6)
                    
            elif '경춘선' in i :
                p5=i[:3]
                if len(i)>3 :
                    p6=i[3:]
                    p6=int(p6)
                    
            elif '신분당선' in i :
                p5=i[:4]
                if len(i)>4 :
                    p6=i[4:]
                    p6=int(p6)
            
            elif '분당선' in i :
                p5=i[:3]
                if len(i)>3 :
                    p6=i[3:]
                    p6=int(p6)
            
            danji_apt_copy=danji_apt_geo.copy()
            danji_apt_geo=g(p5, p6)
            danji_apt_copy=danji_apt_geo.copy()
            namelists2=namelists2+str(i)+', '
            subway_check+=1
            
        if '종합병원거리' in i :
            p7=i[6:]
            p7=int(p7)
            danji_apt_geo=h(p7)
            danji_apt_copy=danji_apt_geo.copy()
            namelists2=namelists2+str(i)+', '
            
        if '대규모점포거리' in i :
            p8=i[7:]
            p8=int(p8)
            danji_apt_copy=danji_apt_geo.copy()
            danji_apt_geo=huge(p8)
            del danji_apt_geo['index']
            danji_apt_copy=danji_apt_geo.copy()
            namelists2=namelists2+str(i)+', '
            huge_check+=1
            
        if '고등학교거리' in i :
            p9=i[6:] 
            p9=int(p9)
            danji_apt_geo=f(p9)
            danji_apt_copy=danji_apt_geo.copy()
            namelists2=namelists2+str(i)+', '
    
    print('\n\n조건 필터링 끝!\n')
    
    if cir==0 :
        before_len=len(danji_apt_geo_final3)
    else : 
        before_len=after_len
        
    after_len=len(danji_apt_geo)
    print(f'필터링 전 아파트 개수 : {before_len}, 필터링 후 아파트 개수 : {after_len}\n')
    
    namelists= namelists + ', 수정 및 추가된 조건_' + namelists2
    
    s = s + condition
    
    cir+=1
    
    answer=input('어떠신가요? 이제 맘에 드시나요? (번호를 입력해주세요!) 1. 아니요, 더 필터링을 거쳐야겠습니다   2. 네, 딱 좋습니다!   3. 헉! 너무 줄었어요. 이전으로 돌려주세요!\n')
    
    if answer=='3' :
        danji_apt_geo=save_df.copy()
        danji_apt_copy=save_df.copy()
        after_len=len(danji_apt_geo)
        
print('이제 모든 필터링이 끝났습니다!')

if cir>0 :
    namelists=namelists[:-2]

# 대규모 점포 조건이 있는지 따져보기

if (huge_check!=0) & (subway_check!=0) :
    danji_apt_geo_final3=danji_apt_geo_final3[['PNU', '주소(시군구)', '주소(읍면동)', '건물 이름', 'k-전체동수', '세대수', '경과연수', '지하철거리', '주변 지하철 역', '환승역 유무','초등학교거리', '중학교거리', '고등학교거리', '종합병원거리', '주요 공원 거리', '대규모 점포','주변 대규모 상가 이름', '주변 대규모 상가 개수','450m 반경 내 아파트 세대수(해당 아파트 포함)', '직장 통근시간', '가장 최근 실거래가', '거래 금액', 'k-복도유형', 'k-난방방식','k-전용면적별세대현황(60㎡이하)', 'k-전용면적별세대현황(60㎡~85㎡이하)', 'k-85㎡~135㎡이하', 'k-135㎡초과', '좌표X', '좌표Y', 'geometry']]

elif (huge_check!=0) & (subway_check==0) :
    danji_apt_geo_final3=danji_apt_geo_final3[['PNU', '주소(시군구)', '주소(읍면동)', '건물 이름', 'k-전체동수', '세대수', '경과연수', '지하철거리', '초등학교거리', '중학교거리', '고등학교거리', '종합병원거리', '주요 공원 거리', '대규모 점포','주변 대규모 상가 이름', '주변 대규모 상가 개수','450m 반경 내 아파트 세대수(해당 아파트 포함)', '직장 통근시간', '가장 최근 실거래가', '거래 금액', 'k-복도유형', 'k-난방방식','k-전용면적별세대현황(60㎡이하)', 'k-전용면적별세대현황(60㎡~85㎡이하)', 'k-85㎡~135㎡이하', 'k-135㎡초과', '좌표X', '좌표Y', 'geometry']]

elif (huge_check==0) & (subway_check!=0) :
    danji_apt_geo_final3=danji_apt_geo_final3[['PNU', '주소(시군구)', '주소(읍면동)', '건물 이름', 'k-전체동수', '세대수', '경과연수', '지하철거리', '주변 지하철 역', '환승역 유무','초등학교거리', '중학교거리', '고등학교거리', '종합병원거리', '주요 공원 거리', '450m 반경 내 아파트 세대수(해당 아파트 포함)', '직장 통근시간', '가장 최근 실거래가', '거래 금액', 'k-복도유형', 'k-난방방식','k-전용면적별세대현황(60㎡이하)', 'k-전용면적별세대현황(60㎡~85㎡이하)', 'k-85㎡~135㎡이하', 'k-135㎡초과', '좌표X', '좌표Y', 'geometry']]

else :
    danji_apt_geo_final3=danji_apt_geo_final3[['PNU', '주소(시군구)', '주소(읍면동)', '건물 이름', 'k-전체동수', '세대수', '경과연수', '지하철거리', '초등학교거리', '중학교거리', '고등학교거리', '종합병원거리', '주요 공원 거리','450m 반경 내 아파트 세대수(해당 아파트 포함)', '직장 통근시간', '가장 최근 실거래가', '거래 금액', 'k-복도유형', 'k-난방방식','k-전용면적별세대현황(60㎡이하)', 'k-전용면적별세대현황(60㎡~85㎡이하)', 'k-85㎡~135㎡이하', 'k-135㎡초과', '좌표X', '좌표Y', 'geometry']]

# danji_apt_geo_final3.to_csv(r'D:\부동산 빅데이터 분석 스터디\아파트 찾기 프로젝트 수정\중간 저장.csv', encoding='cp949')

# danji_apt_geo_final3=pd.read_csv(r'D:\부동산 빅데이터 분석 스터디\아파트 찾기 프로젝트 수정\중간 저장.csv', encoding='cp949')
# del danji_apt_geo_final3['Unnamed: 0']

#%% 
# folium으로 검색기 결과 나온 아파트 띄워보기

lat = danji_apt_geo_final3['좌표Y'].median()
long = danji_apt_geo_final3['좌표X'].median()

m = folium.Map([lat,long],zoom_start=12)

for i in danji_apt_geo_final3.index:
    sub_lat =  danji_apt_geo_final3.loc[i,'좌표Y']
    sub_long = danji_apt_geo_final3.loc[i,'좌표X']
    
    if len(danji_apt_geo_final3.loc[i, '거래 금액'])>1 :
        title = danji_apt_geo_final3.loc[i,'가장 최근 실거래가'] + ' / 거래금액 : ' + danji_apt_geo_final3.loc[i, '거래 금액']
    
    else :
        title= danji_apt_geo_final3.loc[i, '가장 최근 실거래가']
  
    color = 'blue'
    iframe=folium.IFrame(title, width=450, height=60)
    popup=folium.Popup(iframe)
    folium.Marker([sub_lat,sub_long], popup=popup, icon=folium.Icon(icon='home', color=color)).add_to(m)

m.save('dnji_apt_search.html')

#%%

# 파일 저장

danji_apt_geo_final3.to_csv('D:/부동산 빅데이터 분석 스터디/아파트 찾기 프로젝트 수정'+'/'+namelists+' csv.csv', encoding='cp949')
danji_apt_geo_final3.to_excel('D:/부동산 빅데이터 분석 스터디/아파트 찾기 프로젝트 수정'+'/'+namelists+' 엑셀.xlsx', encoding='cp949')

# excel로 조건 추가해서 최종 파일 완성

sem=danji_apt_geo_final3.count()[0]+2
nono='A'+str(sem)

excel_document = openpyxl.load_workbook('D:/부동산 빅데이터 분석 스터디/아파트 찾기 프로젝트 수정'+'/'+namelists+' 엑셀.xlsx')
sheet = excel_document.get_sheet_by_name('Sheet1')

conditions = '조건 :'
for i in s :
    conditions = conditions+' '+i

sheet[nono]=conditions

save_name=namelists+'조건 셀 추가.xlsx'
path='D:/부동산 빅데이터 분석 스터디/아파트 찾기 프로젝트 수정/'
excel_document.save(path+save_name)

#%%

# 서울 지도와 지하철, 아파트, 대규모상가 plot으로 띄워보기

seoul_area=gpd.GeoDataFrame.from_file(r'D:\부동산 빅데이터 분석 스터디\아파트 찾기 프로젝트 수정\geopandas 소방서 띄우기\LARD_ADM_SECT_SGG_11.shp', engine='python', encoding='utf-8')
seoul_area=seoul_area.to_crs(epsg5181_qgis)

# 서울 지도 + 지하철 위치 + 아파트 위치 + 대규모상가 위치 plot으로 띄우기
mini1=mini1.drop_duplicates(subset='geometry')
mini2=mini2.drop_duplicates(subset='geometry')

ax = seoul_area.plot(column="SGG_NM", figsize=(8,8), alpha=0.8)
mini1.boundary.plot(ax=ax, marker='*', color='black', label='subway(700m)', markersize=50)
danji_apt_geo_final.plot(ax=ax, marker='v', color='blue', label='Apt', markersize=100)
mini2.centroid.plot(ax=ax, marker='o', color='red', label='Huge Sangga', markersize=12)
ax.set_title("The best Apts that meet your conditions", fontsize=20)
plt.legend()
plt.show()

#%%

# 해당 아파트가 속한 동 포함 그 주변 동을 조회해보자. 그 다음 kmeans 돌린 후 같은 집단으로 나온 애들만 뽑고 그 아파트들의 가장 최근 실거래가를 나타낼거임.
# 법정동 shp 파일 불러오기.

# bjd_gpd=gpd.GeoDataFrame.from_file(r'C:\Users\user\OneDrive\바탕 화면\부동산 빅데이터 분석 스터디\과제\5주차 수업 과제\AL_00_D001_20210310 법정동 경계\AL_00_D001_20210310(EMD)\AL_00_D001_20210310(EMD).shp', encoding='cp949')
# bjd_gpd['시 코드']=bjd_gpd['A1'].str[:2]
# bjd_gpd=bjd_gpd[bjd_gpd['시 코드']=='11']

# def dong_around_search(dong_nm, level):
#     myself=bjd_gpd.loc[bjd_gpd['A2']==dong_nm]
    
#     for i in range(level) :
#         myself=gpd.sjoin(bjd_gpd, myself[['geometry']], op='intersects')
#         myself=myself.drop_duplicates(subset='A2')
#         myself.drop('index_right', axis=1, inplace=True)
            
#     return myself

# dan_count=len(danji_apt_geo_final3)

# width_count=1
# count=0

# apart_input=input('검색기 결과 중 주변 아파트를 조회해보고 싶은 아파트 이름을 입력해주세요\n')
# dong_input=input('입력하신 아파트의 법정동을 입력해주세요\n')

# while count<7 :
#     dong_around=dong_around_search(dong_input, width_count)
#     width_count+=1
#     # dong_around.plot()
    
#     around_dong_list=list(dong_around['A1']+'00')
    
#     danji_apt_around=danji_apt_machine.copy()
#     danji_apt_around=danji_apt_around[danji_apt_around['년월']==1]
    
#     danji_apt_machine['10자리 코드']=danji_apt_machine['법정동 구 코드']+danji_apt_machine['법정동 동 코드 ']
    
#     # 신길동(예시) 주변 동에 속한 아파트 모두 추출
#     for j in around_dong_list :    
#         fucking=danji_apt_machine[danji_apt_machine['10자리 코드']==j]
#         danji_apt_around=pd.concat([danji_apt_around, fucking])
    
#     count=len(danji_apt_around)
    
# danji_apt_around['x_meter']=''
# danji_apt_around['y_meter']=''
# danji_apt_around= danji_apt_around.reset_index()
# del danji_apt_around['index']

# for i in range(count) :
#     danji_apt_around.loc[i, 'x_meter']=danji_apt_around['geometry'][i].coords.xy[0][0]
#     danji_apt_around.loc[i, 'y_meter']=danji_apt_around['geometry'][i].coords.xy[1][0]

# kmeans_df=danji_apt_around[['x_meter', 'y_meter']]
# kmeans_df=kmeans_df.rename(columns={'x_meter' : 'x', 'y_meter' : 'y'})

# # # plot 띄워보기
# # ax=dong_around.plot(column="A2", figsize=(8,8), alpha=0.8)
# # danji_apt_around.plot(ax=ax, marker='*', color='black', markersize=10)

# distortions = [] #엘보우값 담을 빈 리스트 생성
# K = range(1,8) 
# for k in K:
#     kmeanModel = KMeans(n_clusters=k) 
#     kmeanModel.fit(kmeans_df) 
#     distortions.append(kmeanModel.inertia_)

# # plt.plot(K, distortions, 'bx-')
# # plt.xlabel('k')
# # plt.ylabel('Distortion')
# # plt.title('The plt')

# # elbow 라이브러리
# from yellowbrick.cluster import KElbowVisualizer
# model = KMeans()
# visualizer = KElbowVisualizer(model, k=(1,10))
# visualizer.fit(kmeans_df)
# proper_k=visualizer.elbow_value_ # elbow 값을 구해줌

# ktest = KMeans(n_clusters=proper_k+1) # 넉넉하게 라이브러리에서 구해준 elbow point 값에서 +1를 더해서 그룹화시키자
# ktest.fit(kmeans_df) 
# y_pred = ktest.predict(kmeans_df) 
# # plt.scatter(kmeans_df['x'], kmeans_df['y'], c=y_pred, cmap=plt.cm.Paired) 
# # plt.show()

# danji_apt_around['category']=y_pred

# # 해당 아파트를 기준으로 같은 집단에 있는 아파트만 추출, 해당 아파트의 category 값 입력

# category_find=danji_apt_around.loc[danji_apt_around['건물 이름'].str.contains(apart_input), 'category'].values[0]
# danji_apt_around_final=danji_apt_around.loc[danji_apt_around['category']==category_find]

# 똑같이 실거래가 과정 거친 다음에
# ax=dong_around.plot(column="A2", figsize=(8,8), alpha=0.8)
# danji_apt_around_final2.plot(ax=ax, marker='*', color='black', markersize=10)
#%%

# 사실 DBSCAN이나 KMEANS를 통해서 주변 아파트를 찾는 것 보다 깔끔하게 해당 아파트로부터 반경 1KM이내 아파트 검색해서 실거래가 띄우는게 더 좋긴 함.
# 아파트 이름을 입력하면 해당 아파트로부터 반경 1KM이내에 있는 아파트를 조회하고 그 아파트들의 실거래가를 출력하도록 해보자.

apart_input=input('검색기 결과 중 주변 아파트를 조회해보고 싶은 아파트 이름을 입력해주세요\n')
dong_input=input('입력하신 아파트의 법정동을 입력해주세요\n')
gu_input=input('입력하신 아파트의 구 이름을 입력해주세요\n')

apt_name_df=danji_apt_machine[danji_apt_machine['건물 이름']==apart_input]
apt_name_df=apt_name_df.drop_duplicates(subset='건물 이름')
apt_1km=gpd.GeoDataFrame(apt_name_df, geometry=apt_name_df.buffer(1000).geometry)

danji_apt_1km=gpd.sjoin(danji_apt_machine, apt_1km[['geometry']], how='inner', op='intersects')

danji_apt_1km=danji_apt_1km.drop_duplicates(subset='건물 이름')

#%%
# pnu 만들기

for i in danji_apt_1km.index :
    sep=danji_apt_1km.loc[i, '건물 이름'].split('(')[0]
    danji_apt_1km.loc[i, '건물 이름']=sep
    

def find_xy(searching) :
    url= "https://dapi.kakao.com/v2/local/search/keyword.json?query={}".format(searching)
    headers={"Authorization": "KakaoAK 1f26ccd78d132c1a8df33f46e92cabce"}
    places=requests.get(url,headers=headers).json()['documents']
    
    try :
        place=places[0]        
        jibeon=place['address_name'].split(' ')[3]
        
    except :
        jibeon=np.nan
        
    return jibeon

empty=[]

for i in danji_apt_1km.index :
    empty.append(find_xy(danji_apt_1km.loc[i,'건물 이름']))

jibeon_df=pd.DataFrame(empty)
danji_apt_1km.insert(loc=3,column='Jibeon',value=jibeon_df)

#%%
for_pnu=pd.read_csv(r'D:\부동산 빅데이터 분석 스터디\상권 프로젝트 수정\상권 프로젝트\상권 프로젝트\소상공인시장진흥공단_상가(상권)정보_서울.csv', engine='python', encoding='utf-8', sep='|')
for_pnu=for_pnu.drop_duplicates(subset='법정동코드')

bjdcode_list=[]

for i in danji_apt_1km.index :
    for j in for_pnu.index :
        if danji_apt_1km.loc[i, '주소(읍면동)'] == for_pnu.loc[j, '법정동명'] :
            bjdcode_list.append(str(for_pnu.loc[j, '법정동코드']))
bjd_df=pd.DataFrame(bjdcode_list)
danji_apt_1km.insert(loc=3, column='법정동코드', value=bjd_df)

for i in danji_apt_1km.index :
    if '-' in danji_apt_1km.loc[i, 'Jibeon'] :
        danji_apt_1km.loc[i, 'bonbeon']=danji_apt_1km.loc[i, 'Jibeon'].split('-')[0].zfill(4)
        danji_apt_1km.loc[i, 'boobeon']=danji_apt_1km.loc[i, 'Jibeon'].split('-')[1].zfill(4)
    else :
        danji_apt_1km.loc[i, 'bonbeon']=danji_apt_1km.loc[i, 'Jibeon'].zfill(4)
        danji_apt_1km.loc[i, 'boobeon']='0000'
    
    danji_apt_1km.loc[i, 'PNU']=danji_apt_1km.loc[i, '법정동코드']+'1'+danji_apt_1km.loc[i, 'bonbeon']+danji_apt_1km.loc[i, 'boobeon']

danji_apt_1km['법정동 구 코드']=danji_apt_1km['법정동코드'].str[:5]

#%%

# 앞에서 만들었던 sexy_poor2를 이용해서 xml의 법정동을 가지고 법정동 코드를 생성.
# 국토교통부 아파트 실거래가 Api를 이용해서 실거래가 컬럼 추가하기

# 202103, 202102, 202101.... 이렇게 역순으로 내려가면서 해당 아파트 실거래가가 있을때 그 달의 가장 늦은 날짜의 실거래가를 저장하고 for 문을 break 하는 방식으로 해야할 듯

empty_moong={'가장 최근 실거래가' : [], '거래 금액' : [], '금액' : []}
dict_sig={}

for moong1, moong2, moong3 in zip(danji_apt_1km['법정동 구 코드'], danji_apt_1km['건물 이름'], danji_apt_1km['PNU']):
    print(f'{moong2} 실거래가 받아오는중...')
    month_list=['202103', '202102', '202101', '202012', '202011', '202010', '202009', '202008', '202007', '202006', '202005', '202004', '202003']
    a=pd.DataFrame(columns=['Year', 'Month','Day','Apart','Floor','Area','Price', 'Dong', 'Bonbeon', 'Boobeon', 'Dongcode'])
    apart_name=moong2
    apart_name2=apart_name[:].replace(" ", "")
    sexy_count2=0 # 월별로 해당 아파트의 거래가 있는지 체크하기 위한 변수
    sig_number=moong1
    
    for m in month_list :
        if moong1 not in dict_sig.keys() :
            dict_sig[moong1]={}
            servicekey=''
            url='http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade?LAWD_CD={}&DEAL_YMD={}&serviceKey={}'.format(moong1, m, servicekey)
            
            res=requests.get(url)
            dict_sig[moong1][m]={}
            dict_sig[moong1][m]=BeautifulSoup(res.content, 'xml')
            soup=BeautifulSoup(res.content, 'xml')
        
        else :
            if m in dict_sig[moong1].keys() :
                soup=dict_sig[moong1][m]
            else : 
                servicekey=''
                url='http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade?LAWD_CD={}&DEAL_YMD={}&serviceKey={}'.format(moong1, m, servicekey)

                res=requests.get(url)
                dict_sig[moong1][m]={}
                dict_sig[moong1][m]=BeautifulSoup(res.content, 'xml')
                soup=BeautifulSoup(res.content, 'xml')
        
        
        finding=soup.find_all('item')
        my_dict = {"Year":[],"Month":[],"Day":[],"Apart":[],"Floor":[],"Area":[],"Price":[], "Dong" : [], "Bonbeon" : [], "Boobeon" : [], "Dongcode" : []}

        # finding을 for문 돌려서 출력되는 아파트, 층, 전용면적, 거래금액을 dictionary의 value로 추가하기.
    
        for i in finding :
            year=i.find('년').text.strip()
            
            month=i.find('월').text.strip()

            day=i.find('일').text.strip()

            apart=i.find('아파트').text.strip()

            floor=i.find('층').text.strip()

            area=i.find('전용면적').text.strip()

            price=i.find('거래금액').text.strip()
            
            dong=i.find('법정동').text.strip()
            try : # 지번이 없는게 있음
                jibeon=i.find('지번').text.strip()
            except :
                jibeon='0000'
            
            if '-' in jibeon :
                bonbeon=jibeon[:jibeon.index('-')].zfill(4)
                boobeon=jibeon[jibeon.index('-')+1:].zfill(4)
            else :
                bonbeon=jibeon.zfill(4)
                boobeon='0000'
                
            for i in sexy_poor2.index :
                if dong==sexy_poor2.loc[i, '법정동명']:
                    dongcode=str(sexy_poor2.loc[i, '법정동코드'])[5:] # xml에서는 법정동코드가 없기 때문에 법정동명과 법정동코드가 있는 파일과 매칭해서 법정동 코드를 가져옴
                    break
                
                else :
                    dongcode='00000'
                    
            my_dict["Year"].append(year)
            my_dict["Month"].append(month)
            my_dict["Day"].append(day)
            my_dict["Apart"].append(apart)
            my_dict["Floor"].append(floor)
            my_dict["Area"].append(area)
            my_dict["Price"].append(price)
            my_dict["Dong"].append(dong)
            my_dict["Bonbeon"].append(bonbeon)
            my_dict["Boobeon"].append(boobeon)
            my_dict["Dongcode"].append(dongcode)


        apart_data=pd.DataFrame.from_dict(my_dict)
        
        apart_data['PNU']=moong1+apart_data['Dongcode']+'1'+apart_data['Bonbeon']+apart_data['Boobeon']
        apart_data['PNU']= apart_data['PNU'].astype(str)
        
        b=apart_data.loc[(apart_data['Apart'].str.contains(apart_name)) | apart_data['Apart'].str.contains(apart_name2) | apart_data['PNU'].str.contains(moong3)]
        b['Area']=b['Area'].astype(float)

        if pyung=='A' : # 29평 이하 선택시에 실행
            c=b.loc[(b['Area']<=76) & (b['Area']>58)]

        elif pyung=='B' : # 30평 이상 39평 이하 선택시에 실행
            c=b.loc[(b['Area']>76) & (b['Area']<103)]
            
        else : # 40평 이상 선택시에 실행
            c=b.loc[(b['Area']>=103) & (b['Area']<125)]
        
        sexy_count1=c['Apart'].count() # 조건에 부합하는 아파트가 있는지 확인하기 위함
        if sexy_count1>0 :
            sexy_count2+=1 # 조건에 부합하는 아파트가 있다면 월별 카운트를 +1
            d=c.drop_duplicates('Month', keep='last')
            a=pd.concat([d,a])
            break
        
    if sexy_count2>0 : 
        price_final=a.drop_duplicates(subset='Apart', keep='first')
        price_final['Area']=price_final['Area'].astype(str)
        if len(price_final)>1 :
            price_final=price_final.iloc[[0]]
        
        price_length= len(price_final['Price'].values[0])
        
        if price_length==7 :
            front=price_final['Price'].values[0][:2]
            behind=price_final['Price'].values[0][2:]
            
        elif price_length==6 :
            front=price_final['Price'].values[0][:1]
            behind=price_final['Price'].values[0][1:]
    
        empty=''
        empty2=''
        empty3=''
        
        for index, row in price_final.iterrows() :
            empty=empty+row['Year']+'년 '+row['Month']+'월 '+row['Day']+'일 / '+row['Apart']+' '+row['Floor']+ '층 / 전용면적 : ' + row['Area']+ ' m2 / 거래금액 : ' + front + '억 '+ behind + '만원'
            empty2= front + '억 ' + behind + '만원'
            empty3= int(front)*100000000+int(behind[0])*10000000+int(behind[2:])*10000
            
        empty_moong['가장 최근 실거래가'].append(empty)
        empty_moong['거래 금액'].append(empty2)
        empty_moong['금액'].append(empty3)
    
    else : # 2020.03부터 한번이라도 거래된적이 없음
        empty_moong['가장 최근 실거래가'].append(f'{apart_name} / 1년간 거래 없음')
        empty_moong['거래 금액'].append('')
        empty_moong['금액'].append(0)


empty_moong_data=pd.DataFrame.from_dict(empty_moong)
danji_apt_1km=danji_apt_1km.reset_index() # concat 하기 위해서 index를 초기화
danji_apt_1km_2=pd.concat([danji_apt_1km, empty_moong_data],axis=1) # concat을 이용해서 index 번호로 가로로 병합
del danji_apt_1km_2['index']
danji_apt_1km_2=danji_apt_1km_2[['년월', '지번 주소 코드', '법정동 구 코드', '법정동 동 코드 ', '주소', '건물 이름', '가장 최근 실거래가', '거래 금액', '금액', '세대수', '450m 반경 내 아파트 세대수(해당 아파트 포함)','경과연수', '지하철거리(m)', '종합병원거리(m)', '초등학교거리(m)', '중학교거리(m)', '고등학교거리(m)', '도시공원거리(m)', '도시공원 면적', '주변 면적당 평균 실거래가', '본건 단위면적당 실거래가', '공동주택공시가격 면적당 중앙값', 'geometry', 'x', 'y']]
danji_apt_1km_2['금액']=danji_apt_1km_2['금액'].astype(float)
danji_apt_1km_2=danji_apt_1km_2.sort_values('금액', ascending=False)
del danji_apt_1km_2['금액']


lat = danji_apt_1km_2['y'].mean()
long = danji_apt_1km_2['x'].mean()

m = folium.Map([lat,long],zoom_start=16)

for i in danji_apt_1km_2.index:
    sub_lat =  danji_apt_1km_2.loc[i,'y']
    sub_long = danji_apt_1km_2.loc[i,'x']
    
    title = danji_apt_1km_2.loc[i,'가장 최근 실거래가']
  
    color = 'blue'
    if danji_apt_1km_2.loc[i, '건물 이름'] == apart_input:
        color = 'red'
        folium.Circle([sub_lat,sub_long], weight=8, color='black', radius = 1000).add_to(m)
        # opacity와 fill=True, fill_opacity를 이용하면 불투명도를 조절할 수 있다.
    iframe=folium.IFrame(danji_apt_1km_2.loc[i,'가장 최근 실거래가'], width=450, height=60)
    popup=folium.Popup(iframe)
    folium.Marker([sub_lat,sub_long], popup=popup, icon=folium.Icon(icon='home', color=color)).add_to(m)

m.save('dnji_apt_1km.html')

#%%

year_list=[2016, 2017, 2018, 2019, 2020]

def original_save(year) :
    csv_file=pd.read_csv(f'C:/Users/user/OneDrive/바탕 화면/부동산 빅데이터 분석 스터디/과제/4주차 수업 과제/서울특별시 2016 ~ 2020 실거래가/서울특별시_부동산_실거래가_정보_{year}년.csv', encoding='cp949', sep=',')
    return csv_file

def make_original_dict() :
    global original_dict
    original_dict={}
    
    for i in year_list :
        original_dict[i]=original_save(i)
    
    return original_dict

# 래미안 옥수 리버젠 아파트가 대입되면 a=['아파트명', '2016 ', '2017 ', '2018 ', '2019 ', 2020 ', '2021 '] 식의 데이터프레임을 만들고
# 2016년도 해당 아파트 평균내서 값 리턴, 만약 2016년에 해당 아파트 실거래가가 없으면 nan값을 전달. 

original_dict=make_original_dict()

sil=pd.read_csv(r'C:\Users\user\OneDrive\바탕 화면\부동산 빅데이터 분석 스터디\과제\5주차 수업 과제\서울특별시_202101_202103_실거래가.csv', encoding='cp949')

def mean_by_year(j, apart_name, apart_name2, pnu) :
    sil_file=original_dict[j].copy()
    sil_file=sil_file[['신고년도', '지번코드', '건물면적', '물건금액', '건물명']]
    sil_file=sil_file.dropna(subset=['건물명'])
    sil_file=sil_file.loc[(sil_file['건물면적']>76) & (sil_file['건물면적']<103)] # 30평대 기준
    sil_file['지번코드']=sil_file['지번코드'].astype(str)
    csv_file2=sil_file.loc[sil_file['건물명'].str.contains(apart_name) | sil_file['건물명'].str.contains(apart_name2) | sil_file['지번코드'].str.contains(pnu)]
    if len(csv_file2)>0 :
        return int(np.mean(csv_file2['물건금액']))
    else :
        return np.nan

def mean_by_year_2(apart_name, apart_name2, pnu) :
    sil_2021=sil.copy()
    del sil_2021['Unnamed: 0']
    sil_2021=sil_2021.rename(columns={'PNU': '지번코드', 'Gu_name' : '자치구명', 'Gu_code' : '시군구코드', 'Dong' : '법정동명', 'Year' : '신고년도', 'Area' : '건물면적', 'Floor' : '층정보', 'Price' : '물건금액', 'Apart' : '건물명'})
    sil_2021=sil_2021[['신고년도', '지번코드', '건물면적', '물건금액', '건물명']]
    sil_2021=sil_2021.loc[(sil_2021['건물면적']>76) & (sil_2021['건물면적']<103)] # 30평대 기준
    sil_2021['지번코드']=sil_2021['지번코드'].astype(str)
    sil_2021=sil_2021.loc[sil_2021['건물명'].str.contains(apart_name) | sil_2021['건물명'].str.contains(apart_name2) | sil_2021['지번코드'].str.contains(pnu)]
    if len(sil_2021)>1 :
        sil_2021['물건금액2']=''
        for i in sil_2021.index :
            price_length=len(sil_2021.loc[i, '물건금액'])
            
            if price_length==7 :
                front=sil_2021.loc[i, '물건금액'][:2]
                behind=sil_2021.loc[i, '물건금액'][2:]
                
            elif price_length==6 :
                front=sil_2021.loc[i, '물건금액'][:1]
                behind=sil_2021.loc[i, '물건금액'][1:]
        
            sil_2021.loc[i, '물건금액2']= int(front)*100000000+int(behind[0])*10000000+int(behind[2:])*10000
        return int(np.mean(sil_2021['물건금액2']))
        
    elif len(sil_2021)==1 :
        sil_2021['물건금액2']=''
        for i in sil_2021.index :
            price_length=len(sil_2021.loc[i, '물건금액'])
            
            if price_length==7 :
                front=sil_2021.loc[i, '물건금액'][:2]
                behind=sil_2021.loc[i, '물건금액'][2:]
                
            elif price_length==6 :
                front=sil_2021.loc[i, '물건금액'][:1]
                behind=sil_2021.loc[i, '물건금액'][1:]
        
            sil_2021.loc[i, '물건금액2']= int(front)*100000000+int(behind[0])*10000000+int(behind[2:])*10000
            
        return int(sil_2021.loc[i, '물건금액2'])
    
    else : 
        return np.nan

for_concat=pd.DataFrame(columns=['지번코드', '건물명', '2016', '2017', '2018', '2019', '2020', '2021'])
for_concat[['2016', '2017', '2018', '2019', '2020', '2021']]=for_concat[['2016', '2017', '2018', '2019', '2020', '2021']].astype(int)


for i in tqdm(danji_apt_1km_2.index) :
    apart_name=danji_apt_1km_2.loc[i, '건물 이름']
    apart_name2=apart_name[:].replace(" ", "")
    pnu=danji_apt_1km_2.loc[i, '지번 주소 코드']
    for_concat.loc[i, '지번코드']=pnu
    for_concat.loc[i, '건물명']=apart_name
    for j in year_list :
        for_concat.loc[i, f'{j}']=mean_by_year(j, apart_name, apart_name2, pnu)

    for_concat.loc[i, '2021']=mean_by_year_2(apart_name, apart_name2, pnu)

for_concat[['2016', '2017', '2018', '2019', '2020', '2021']]=for_concat[['2016', '2017', '2018', '2019', '2020', '2021']].interpolate(method='linear', axis=1)
for_concat=for_concat.dropna(subset=['2016', '2017', '2018', '2019', '2020', '2021'], axis=0, how='all')

for_concat=for_concat.set_index('건물명')
for_concat2=for_concat[['2016', '2017', '2018', '2019', '2020', '2021']].head(10)
for_concat2=for_concat2.transpose()

#%%

# 입력한 아파트 법정동 포함 주변 법정동의 실거래가 평균을 나타내줌

bjd_gpd=gpd.GeoDataFrame.from_file(r'C:\Users\user\OneDrive\바탕 화면\부동산 빅데이터 분석 스터디\과제\5주차 수업 과제\AL_00_D001_20210310 법정동 경계\AL_00_D001_20210310(EMD)\AL_00_D001_20210310(EMD).shp', encoding='cp949')
bjd_gpd['시 코드']=bjd_gpd['A1'].str[:2]
bjd_gpd=bjd_gpd[bjd_gpd['시 코드']=='11']

def dong_around_search(dong_nm, level):
    myself=bjd_gpd.loc[bjd_gpd['A2']==dong_nm]
    
    for i in range(level) :
        myself=gpd.sjoin(bjd_gpd, myself[['geometry']], op='intersects')
        myself=myself.drop_duplicates(subset='A2')
        myself.drop('index_right', axis=1, inplace=True)
            
    return myself

dong_around=dong_around_search(dong_input, 1)
# dong_around.plot()
    
around_dong_list=pd.DataFrame(dong_around['A2'])

def dong_mean_by_year(j, dong_nm) :
    sil_file=original_dict[j].copy()
    sil_file=sil_file[['신고년도', '법정동명', '건물주용도', '건물면적', '물건금액', '건물명']]
    sil_file=sil_file.dropna(subset=['건물명'])
    sil_file=sil_file.loc[(sil_file['건물면적']>76) & (sil_file['건물면적']<103)] # 30평대 기준
    sil_file=sil_file.loc[sil_file['법정동명']==dong_nm]
    sil_file=sil_file.loc[sil_file['건물주용도']=='아파트']
    if len(sil_file)>0 :
        return int(np.mean(sil_file['물건금액']))
    else :
        return np.nan

def dong_mean_by_year_2(dong_nm) :
    sil_2021=sil.copy()
    del sil_2021['Unnamed: 0']
    sil_2021=sil_2021.rename(columns={'PNU': '지번코드', 'Gu_name' : '자치구명', 'Gu_code' : '시군구코드', 'Dong' : '법정동명', 'Year' : '신고년도', 'Area' : '건물면적', 'Floor' : '층정보', 'Price' : '물건금액', 'Apart' : '건물명'})
    sil_2021=sil_2021[['신고년도', '법정동명', '건물면적', '물건금액', '건물명']]
    sil_2021=sil_2021.loc[(sil_2021['건물면적']>76) & (sil_2021['건물면적']<103)] # 30평대 기준
    sil_2021=sil_2021.loc[sil_2021['법정동명']==dong_nm]
    if len(sil_2021)>0 :
        sil_2021['물건금액2']=''
        for i in sil_2021.index :
            price_length=len(sil_2021.loc[i, '물건금액'])
            
            if price_length==7 :
                front=sil_2021.loc[i, '물건금액'][:2]
                behind=sil_2021.loc[i, '물건금액'][2:]
                
            elif price_length==6 :
                front=sil_2021.loc[i, '물건금액'][:1]
                behind=sil_2021.loc[i, '물건금액'][1:]
        
            sil_2021.loc[i, '물건금액2']= int(front)*100000000+int(behind[0])*10000000+int(behind[2:])*10000
        return int(np.mean(sil_2021['물건금액2']))
    
    else :
        return np.nan
    
for_concat_dong=pd.DataFrame(columns=['법정동명', '2016', '2017', '2018', '2019', '2020', '2021'])
for_concat_dong[['2016', '2017', '2018', '2019', '2020', '2021']]=for_concat_dong[['2016', '2017', '2018', '2019', '2020', '2021']].astype(int)

for i in tqdm(around_dong_list.index) :
    for_concat_dong.loc[i, '법정동명']=around_dong_list.loc[i, 'A2']
    for j in year_list :
        for_concat_dong.loc[i, f'{j}']=dong_mean_by_year(j, around_dong_list.loc[i, 'A2'])

    for_concat_dong.loc[i, '2021']=dong_mean_by_year_2(around_dong_list.loc[i, 'A2'])

for_concat_dong[['2016', '2017', '2018', '2019', '2020', '2021']]=for_concat_dong[['2016', '2017', '2018', '2019', '2020', '2021']].interpolate(method='linear', axis=1)
for_concat_dong=for_concat_dong.dropna(subset=['2016', '2017', '2018', '2019', '2020', '2021'], axis=0, how='all')

for_concat_dong=for_concat_dong.set_index('법정동명')
for_concat_dong2=for_concat_dong[['2016', '2017', '2018', '2019', '2020', '2021']].head(10)
for_concat_dong2=for_concat_dong2.transpose()
#%% 
# 마지막은 주변 구 연평균 실거래가 비교 띄우기

seoul_area=gpd.GeoDataFrame.from_file(r'C:\Users\user\OneDrive\바탕 화면\부동산 빅데이터 분석 스터디\과제\3주차 수업 과제\geopandas 소방서 띄우기\LARD_ADM_SECT_SGG_11.shp', engine='python', encoding='utf-8')
seoul_area=seoul_area.dropna()

def gu_around_search(gu_nm, level):
    myself=seoul_area.loc[seoul_area['SGG_NM']==gu_nm]
    
    for i in range(level) :
        myself=gpd.sjoin(seoul_area, myself[['geometry']], op='intersects')
        myself=myself.drop_duplicates(subset='SGG_NM')
        myself.drop('index_right', axis=1, inplace=True)
            
    return myself


gu_around=gu_around_search(gu_input, 1)
# gu_around.plot()
    
around_gu_list=pd.DataFrame(gu_around['SGG_NM'])

for i in around_gu_list.index :
    if '서울시' in around_gu_list.loc[i, 'SGG_NM'] :
        around_gu_list.loc[i, 'SGG_NM']=around_gu_list.loc[i, 'SGG_NM'][3:]

def gu_mean_by_year(j, gu_nm) :
    sil_file=original_dict[j].copy()
    sil_file=sil_file[['자치구명', '신고년도', '법정동명', '건물주용도', '건물면적', '물건금액', '건물명']]
    sil_file=sil_file.dropna(subset=['건물명'])
    sil_file=sil_file.loc[(sil_file['건물면적']>76) & (sil_file['건물면적']<103)] # 30평대 기준
    sil_file=sil_file.loc[sil_file['자치구명']==gu_nm]
    sil_file=sil_file.loc[sil_file['건물주용도']=='아파트']
    if len(sil_file)>0 :
        return int(np.mean(sil_file['물건금액']))
    else :
        return np.nan

def gu_mean_by_year_2(gu_nm) :
    sil_2021=sil.copy()
    del sil_2021['Unnamed: 0']
    sil_2021=sil_2021.rename(columns={'PNU': '지번코드', 'Gu_name' : '자치구명', 'Gu_code' : '시군구코드', 'Dong' : '법정동명', 'Year' : '신고년도', 'Area' : '건물면적', 'Floor' : '층정보', 'Price' : '물건금액', 'Apart' : '건물명'})
    sil_2021=sil_2021[['자치구명', '신고년도', '법정동명', '건물면적', '물건금액', '건물명']]
    sil_2021=sil_2021.loc[(sil_2021['건물면적']>76) & (sil_2021['건물면적']<103)] # 30평대 기준
    sil_2021=sil_2021.loc[sil_2021['자치구명']==gu_nm]
    if len(sil_2021)>0 :
        sil_2021['물건금액2']=''
        for i in sil_2021.index :
            price_length=len(sil_2021.loc[i, '물건금액'])
            
            if price_length==7 :
                front=sil_2021.loc[i, '물건금액'][:2]
                behind=sil_2021.loc[i, '물건금액'][2:]
                
            elif price_length==6 :
                front=sil_2021.loc[i, '물건금액'][:1]
                behind=sil_2021.loc[i, '물건금액'][1:]
        
            sil_2021.loc[i, '물건금액2']= int(front)*100000000+int(behind[0])*10000000+int(behind[2:])*10000
        return int(np.mean(sil_2021['물건금액2']))
    
    else :
        return np.nan

for_concat_gu=pd.DataFrame(columns=['자치구명', '2016', '2017', '2018', '2019', '2020', '2021'])
for_concat_gu[['2016', '2017', '2018', '2019', '2020', '2021']]=for_concat_gu[['2016', '2017', '2018', '2019', '2020', '2021']].astype(int)

for i in tqdm(around_gu_list.index) :
    for_concat_gu.loc[i, '자치구명']=around_gu_list.loc[i, 'SGG_NM']
    for j in year_list :
        for_concat_gu.loc[i, f'{j}']=gu_mean_by_year(j, around_gu_list.loc[i, 'SGG_NM'])

    for_concat_gu.loc[i, '2021']=gu_mean_by_year_2(around_gu_list.loc[i, 'SGG_NM'])

for_concat_gu[['2016', '2017', '2018', '2019', '2020', '2021']]=for_concat_gu[['2016', '2017', '2018', '2019', '2020', '2021']].interpolate(method='linear', axis=1)
for_concat_gu=for_concat_gu.dropna(subset=['2016', '2017', '2018', '2019', '2020', '2021'], axis=0, how='all')

for_concat_gu=for_concat_gu.set_index('자치구명')
for_concat_gu2=for_concat_gu[['2016', '2017', '2018', '2019', '2020', '2021']].head(10)
for_concat_gu2=for_concat_gu2.transpose()

#%%
from matplotlib import font_manager, rc
font_path = 'C:\\Users\\user\\AppData\\Local\\Microsoft\\Windows\\Fonts\\NanumBarunpenR.ttf'
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

apart_count=list(for_concat.index).index(apart_input)
dong_count=list(for_concat_dong.index).index(dong_input)
gu_count=list(for_concat_gu.index).index(gu_input)

plt.figure(figsize= (45, 15))

plt.subplot(131)
count=len(for_concat)
if count>=10 :
    for i in range(10):
        if i!=apart_count :
            plt.plot(for_concat2.index, for_concat2.iloc[:, i], linestyle='-', linewidth=4)
        else :
            plt.plot(for_concat2.index, for_concat2.iloc[:, i], linestyle='--', linewidth=7)
else :
    for i in range(count) :
        if i!=apart_count :
            plt.plot(for_concat2.index, for_concat2.iloc[:, i], linestyle='-', linewidth=4)
        else :
            plt.plot(for_concat2.index, for_concat2.iloc[:, i], linestyle='--', linewidth=7)

plt.title('연도별 아파트 평균 실거래가 / Y축 : 10억 단위', fontsize=30)
plt.legend(for_concat.index, fontsize=20)
plt.xticks(fontsize=22)
plt.yticks(fontsize=22)
plt.xlabel('연도', fontsize=22)
plt.grid()

plt.subplot(132)

count=len(for_concat_dong)
if count>=10 :
    for i in range(10):
        if i!=dong_count :
            plt.plot(for_concat_dong2.index, for_concat_dong2.iloc[:, i], linestyle='-', linewidth=3)
        else :
            plt.plot(for_concat_dong2.index, for_concat_dong2.iloc[:, i], linestyle='--', linewidth=7)
else :
    for i in range(count):
        if i!=dong_count :
            plt.plot(for_concat_dong2.index, for_concat_dong2.iloc[:, i], linestyle='-', linewidth=3)
        else :
            plt.plot(for_concat_dong2.index, for_concat_dong2.iloc[:, i], linestyle='--', linewidth=7)
            
plt.title('연도별 동 평균 실거래가 / Y축 : 10억 단위', fontsize=30)
plt.legend(for_concat_dong.index, fontsize=20)
plt.xticks(fontsize=22)
plt.yticks(fontsize=22)
plt.xlabel('연도', fontsize=22)
plt.grid()

plt.subplot(133)

count=len(for_concat_gu)
if count>=10 :
    for i in range(10):
        if i!=gu_count :
            plt.plot(for_concat_gu2.index, for_concat_gu2.iloc[:, i], linestyle='-', linewidth=3)
        else :
            plt.plot(for_concat_gu2.index, for_concat_gu2.iloc[:, i], linestyle='--', linewidth=7)
else :
    for i in range(count):
        if i!=gu_count :
            plt.plot(for_concat_gu2.index, for_concat_gu2.iloc[:, i], linestyle='-', linewidth=3)
        else :
            plt.plot(for_concat_gu2.index, for_concat_gu2.iloc[:, i], linestyle='--', linewidth=7)
            
plt.title('연도별 구 평균 실거래가 / Y축 : 10억 단위', fontsize=30)
plt.legend(for_concat_gu.index, fontsize=20)
plt.xticks(fontsize=22)
plt.yticks(fontsize=22)
plt.xlabel('연도', fontsize=22)
plt.grid()

plt.savefig(f'{apart_input} 주변 아파트 및 주변 동 평균 실거래가 비교', dpi=200)

#%%

# 입력한 아파트 네이버 부동산 크롤링

os.chdir(r'C:\Users\user\OneDrive\바탕 화면')

wd=webdriver.Chrome('chromedriver.exe')
wd.maximize_window()
wd.implicitly_wait(3)

url='https://new.land.naver.com/complexes?ms=37.462278,126.810925,17&a=APT:ABYG:JGC&e=RETAIL'

wd.get(url)
wd.implicitly_wait(3)

# keyword=input('검색하려는 아파트를 입력하세요 : ')
# 검색 결과 두개 나오는 아파트 필터링 거치기, try except로 하면 될듯
keyword= apart_input

wd.find_element_by_class_name('search_input').send_keys(keyword)
wd.implicitly_wait(2)

wd.find_element_by_class_name('button_search--icon').click()

time.sleep(2)

try :
    wd.find_element_by_xpath('//*[@id="ct"]/div[2]/div[1]/div[2]/div/div/div[1]/div/a').click() # 맨 처음 검색 결과를 클릭
except :
    pass

# 아파트 정보 요약 저장

label_category=wd.find_element_by_class_name('label--category').text

apart_name=wd.find_element_by_id('complexTitle').text

xpath='//*[@id="summaryInfo"]/dl/dd[1]'
sedae=wd.find_element_by_xpath(xpath).text

xpath='//*[@id="summaryInfo"]/dl/dd[2]'
dong=wd.find_element_by_xpath(xpath).text

xpath='//*[@id="summaryInfo"]/dl/dd[3]'
use_permission= wd.find_element_by_xpath(xpath).text

xpath='//*[@id="summaryInfo"]/dl/dd[4]'
area = wd.find_element_by_xpath(xpath).text

# 아파트 정보 요약 전체 출력
 
print(label_category, apart_name, sedae, dong, use_permission, area)

# print(wd.find_element_by_id('summaryInfo').find_element_by_class_name('complex_feature').text)

# 가장 최근 실거래가 정보
try :
    recently_trade_price=wd.find_element_by_class_name('complex_price--trade').find_element_by_class_name('data').text
    recently_trade_date=wd.find_element_by_class_name('complex_price--trade').find_element_by_class_name('date').text
    print('가장 최근 실거래가 : '+recently_trade_price +'\n' + '거래 물건 정보  : ' +recently_trade_date)
    
except :
    pass

# 매물 가격 범위

trade_range_buy=wd.find_element_by_xpath('//*[@id="summaryInfo"]/div[2]/div[1]/div/dl[1]/dd').text
trade_range_burrow=wd.find_element_by_xpath('//*[@id="summaryInfo"]/div[2]/div[1]/div/dl[2]/dd').text

print('매매 매물 가격 범위 : ' + trade_range_buy + '\n' + '전세 매물 가격 범위 : ' + trade_range_burrow + '\n')

wd.find_element_by_xpath('//*[@id="complexOverviewList"]/div/div[1]/div[2]/div/div[1]/button').click()
time.sleep(1)
wd.find_element_by_xpath('//*[@id="complexOverviewList"]/div/div[1]/div[2]/div/div[1]/div/div/ul/li[2]').click()
time.sleep(1)
wd.find_element_by_class_name('address_filter').click()
time.sleep(1)

# 맨 아래까지 스크롤 내리기

a=0
while True :
    sexy=wd.find_element_by_xpath('//*[@id="articleListArea"]/div[last()]')
    wd.execute_script("arguments[0].scrollIntoView();", sexy)
    time.sleep(1)
    if a==wd.execute_script('return document.querySelector(".infinite_scroll").scrollHeight') :
        break
    a=wd.execute_script('return document.querySelector(".infinite_scroll").scrollHeight')

html_src = wd.page_source
soup=BeautifulSoup(html_src, 'html.parser')
items=soup.find_all(class_='item false')

# 매물 정보 출력

price_df=pd.DataFrame()

for j, item in enumerate(items) :
    print(item.find('span', {'class' : 'text'}).text)
    a=item.find('span', {'class' : 'price'}).text
    if len(a) > 3 :
        print(item.find('span', {'class' : 'type'}).text + item.find('span', {'class' : 'price'}).text +'만원')
        price_front=item.find('span', {'class' : 'price'}).text[:2]
        price_behind=item.find('span', {'class' : 'price'}).text[4] + item.find('span', {'class' : 'price'}).text[6:9]
        price=int(price_front)*(10**8) + int(price_behind) * (10**4)
        
    else :
        print(item.find('span', {'class' : 'type'}).text + item.find('span', {'class' : 'price'}).text)
        price=int(item.find('span', {'class' : 'price'}).text[:2]) * (10**8)
        
    specs= item.find_all(class_='spec')
    for i, spec in enumerate(specs) :
        if i==0 :
            p = re.search(r'(/)(\d{2,3})(m)', spec.text.split(' ')[0]).group(2)
            price_df.loc[j, 'Area']=p
            price_df.loc[j, 'Price']=price
            
        print(spec.text)
            
    agent_infos= item.find_all(class_='agent_info')
    for i, agent_info in enumerate(agent_infos) :
        if i==0 :
            print('제공 : ' + agent_info.text)
        else :
            print('중개사무소 : ' + agent_info.text)
    try :
        print(item.find(class_='label label--confirm').text[:-2])
    except :
        pass
    
    print('\n-----------------------------------------------------------------------\n')

# 매물 가격을 box plot으로 나타내기
price_df['Area']=price_df['Area'].astype(int)
price_df=price_df.sort_values(by='Area')

from matplotlib import font_manager, rc
font_path = 'C:\\Users\\user\\AppData\\Local\\Microsoft\\Windows\\Fonts\\NanumBarunpenR.ttf'
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

plt.figure(figsize= (14, 10))

plt.subplot(121)
sns.boxplot(x="Area", y="Price", data=price_df)
plt.xlabel('전용면적(m2)', fontsize=20)
plt.ylabel('매도호가 (10억 단위)', fontsize=20)
plt.title('Boxplot of Price', fontsize=20)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.grid()


plt.subplot(122)
plt.hist(price_df['Area'], rwidth=0.7)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.xlabel('전용면적(m2)', fontsize=20)
plt.ylabel('빈도수', fontsize=20)
plt.grid()
plt.title('Histogram of Area', fontsize=20)

#%%

import re
from konlpy.tag import Hannanum, Kkma, Twitter, Komoran, Mecab
from wordcloud import WordCloud
from collections import Counter

os.chdir(r'C:\Users\user\OneDrive\바탕 화면')

apart_input=input('검색하고싶은 아파트를 입력해주세요 : ')

wd=webdriver.Chrome('chromedriver.exe')
wd.maximize_window()
wd.implicitly_wait(3)

url='https://hogangnono.com/'

wd.get(url)
time.sleep(1)

wd.find_element_by_class_name('css-4js02h').click()
time.sleep(0.5)
wd.find_element_by_xpath('//*[@id="container"]/div[3]').click()
time.sleep(1)
wd.find_element_by_class_name('css-ovwgyn').click()
time.sleep(1)

wd.switch_to_window(wd.window_handles[1])
time.sleep(1)
wd.find_element_by_xpath('//*[@id="id_email_2"]').send_keys('')
wd.find_element_by_id('id_password_3').send_keys('')
time.sleep(0.5)

wd.find_element_by_xpath('//*[@id="login-form"]/fieldset/div[8]/button[1]').click()
time.sleep(1)

wd.switch_to_window(wd.window_handles[0])

wd.find_element_by_xpath('//*[@id="base-header"]/a[1]/span/span/span').click() # 내 메뉴 창 닫기

def find_dong(searching) :
    url= "https://dapi.kakao.com/v2/local/search/keyword.json?query={}".format(searching)
    headers={"Authorization": "KakaoAK 1f26ccd78d132c1a8df33f46e92cabce"}
    places=requests.get(url,headers=headers).json()['documents']
    place=places[0]
    name=place['place_name']
    address=place['address_name']
    p = re.search(r'(\s)(\w{1,5}동)', address).group(2)
    data=[name, p]
    return data

text_dong=find_dong(apart_input)[1]
text_apart=find_dong(apart_input)[0]

keyword=text_dong + ' ' + apart_input
wd.find_element_by_class_name('keyword').send_keys(keyword)
time.sleep(1)
wd.find_element_by_class_name('btn-search').click()
time.sleep(1)

apart_list=wd.find_element_by_xpath('//*[@id="container"]/div[4]/div/div/div[1]/div/ul').text.split('\n') # li를 검색하 모든 태그를 안가져오고 하나만 가져올까?
apart_list=[j for i, j in enumerate(apart_list) if i%2==0]

point_df=pd.DataFrame(columns=['count'])

for count, j in enumerate(apart_list) :
    non_space=j[:]
    j=j.split(' ')[0]
    point=0
    for i in text_dong :
        if i in j :
            point+=1
    for i in text_apart :
        if i in non_space.split(' ')[1] :
            point+=1
            
    point_df.loc[count, 'count']=int(point)

point_max_index=np.argmax(point_df)+1

wd.find_element_by_xpath(f'//*[@id="container"]/div[4]/div/div/div[1]/div[1]/ul/li[{point_max_index}]/a').click()
time.sleep(1)

wd.find_element_by_class_name('comment').click()
time.sleep(2)

wd.find_element_by_xpath('//*[@id="base-header"]/a[3]').click() # 이야기 상세검색 조건 클릭
time.sleep(2)

condition='장점, 단점, 커뮤니티, 접근성, 공원, 신축, 구축, 운동, 산책, 편의시설, 주민, 안전, 보안, 경관, 경치, 야경, 재건축, 경비, 노후, 자동차, 수납공간, 버스, 대형마트, 냄새, 녹물, 출퇴근, 언덕, 호재, 안전, 방음, 간격, 구조, 아이, 악재, 주차, 만족, 대로변, 문제, 불편, 교통, 상권, 상가, 학군, 학교, 소음, 학원, 지하철, 자가용, 고속도로, 조경, 병원'

wd.find_element_by_xpath('//*[@id="base-header"]/h2/span/div/form/input').send_keys(condition)
time.sleep(1)

wd.find_element_by_xpath('//*[@id="base-header"]/a[2]').click() # 조건 입력 후 클릭
time.sleep(2)

a=0

start=time.time()

for _ in tqdm(range(75)) : # 최대 300개까지만 띄워서 분석하는게 나을듯
    try :
        sexy=wd.find_element_by_xpath('//*[@id="container"]/div[4]/div[2]/div/div[2]/div[1]/div[2]/div/div[1]/a')
        wd.execute_script("arguments[0].scrollIntoView();", sexy)
        time.sleep(1)
        wd.execute_script("arguments[0].click();", sexy)
        time.sleep(1)
    
        if a==wd.execute_script('return document.querySelector("div.css-111v2fw > div.css-0").scrollHeight') :
            break
        a=wd.execute_script('return document.querySelector("div.css-111v2fw > div.css-0").scrollHeight')
    
    except :
        break

end=time.time()

print((end-start)/60)

html_src = wd.page_source
soup=BeautifulSoup(html_src, 'html.parser')
comment=soup.find(class_='css-111v2fw').find_all(class_='css-cqdvbr')

extractor = Hannanum() # 얘를 써서 word 지도를 만들자!

nouns = []

for i in comment :
    if len(i.text) > 1 :
        if ('더보기' in i.text) & ('삭제되었습니다' not in i.text) :
            # print(i.text[:-3], end='\n\n')
            nouns.extend(extractor.nouns(i.text))
            
        elif '삭제되었습니다' not in i.text:
            # print(i.text, end='\n\n')
            nouns.extend(extractor.nouns(i.text))
        

count=Counter(nouns)
words=dict(count.most_common())

for word in list(words.keys()) :
    if len(word) == 1:
        del words[word]
        continue # 자기 아래에 있는 코드 무시하고 for문 반복
    if (word=='아파트') | (word=='저녁') | (word=='댓글') |(word=='지금') | (word=='기분') | (word=='4억') | (word=='관심') | (word=='이곳') | (word=='너무좋고') |(word=='얼마전') |(word=='정확') | (word=='이전') | (word=='좋을꺼같습니') |(word=='추천드') |(word=='느낌') |(word=='3억') |(word=='2억') |(word=='1억') |(word=='나름') |(word=='초중반') |(word=='거리') |(word=='실제') |(word=='우리아파트') |(word=='단지') | (word=='진행') |(word=='12') |(word=='내년') |(word=='시간') |(word=='1차') |(word=='3차') | (word=='2차') |(word=='부분') |(word=='11') | (word=='거리') |(word=='주변') |  (word=='만큼') |(word=='임장와보시') | (word=='예전') | (word=='ㅠㅠ') | (word=='어떤가요') | (word=='대부분') | (word=='단지내') |  (word=='좋아지길') | (word=='장보') | (word=='3월') | (word=='2월') | (word=='1월') | (word=='다섯') | (word=='넷') | (word=='셋') | (word=='둘') | (word=='하나') | (word=='신구') | (word=='최대') |(word=='무엇') |  (word=='자체') | (word=='포함') | (word=='일부') | (word=='단지') |(word=='궁금') | (word=='정도') | (word=='단지별') | (word=='입주민') | (word=='어디') | (word=='1.') | (word=='2.') | (word=='3.') | (word=='4.') | (word=='5.') | (word=='6.') | (word=='가능') | (word=='생각') | (word=='최대') | (word=='위치해') | (word=='더보') | (word=='1개') | (word=='2개') | (word=='3개') | (word=='곳곳') | (word=='예상') | (word=='1년') | (word=='2년') | (word=='3년') | (word=='4년') :
        del words[word]
        continue
        
    if words[word]==1:
        del words[word]
    
        
wc = WordCloud(
    font_path='C:\\Users\\user\\AppData\\Local\\Microsoft\\Windows\\Fonts\\NanumBarunpenR.ttf',
    width=2000,
    height=1000).generate_from_frequencies(words)

from matplotlib import font_manager, rc
font_path = 'C:\\Users\\user\\AppData\\Local\\Microsoft\\Windows\\Fonts\\NanumBarunpenR.ttf'
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

plt.figure(figsize=(20, 10))
plt.imshow(wc)
plt.axis('off')
plt.title(f'{apart_input} 검색 결과입니다!', fontsize=40)
plt.show()

