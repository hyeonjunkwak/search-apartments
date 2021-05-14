# -*- coding: utf-8 -*-
"""
Created on Tue May 11 01:56:26 2021

@author: user
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, MultiPoint
from shapely.geometry import MultiPolygon, JOIN_STYLE
import matplotlib.pyplot as plt
from tqdm import tqdm
from fiona.crs import from_string
from pyproj import CRS

epsg5181_qgis = from_string("+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=500000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs")

school=pd.read_csv(r'D:\부동산 빅데이터 분석 스터디\new\서울특별시 학교 기본정보.csv', encoding='cp949')

school=school.drop_duplicates(subset='표준학교코드')
school=school[~school['학교명'].str.contains('미사용')]

school=school[school['학교종류명'].str.contains('초등학교|중학교|고등학교')]
school=school[(school['학교종류명']=='초등학교') | (school['학교종류명']=='중학교') | (school['학교종류명']=='고등학교')]
school=school[school['관할조직명']!='교육부']

def find_xy(searching) :
    url= "https://dapi.kakao.com/v2/local/search/keyword.json?query={}".format(searching)
    headers={"Authorization": "KakaoAK 1f26ccd78d132c1a8df33f46e92cabce"}
    places=requests.get(url,headers=headers).json()['documents']
    try :
        place=places[0]
        
        school_x=float(place['x'])
        school_y=float(place['y'])
        data=[school_x, school_y]
        
    except :
        data=[np.nan, np.nan]
        
    return data

for i in tqdm(school.index) :
    if school.loc[i, '학교명'] in '서울' :
        school_name=school.loc[i, '학교명']
    else :
        school_name= '서울 ' + school.loc[i, '학교명']
        
    xy=find_xy(school_name)

    school.loc[i, 'x']=xy[0]
    school.loc[i, 'y']=xy[1]

school=school.dropna(subset=['x'])

school.to_csv(r'D:\부동산 빅데이터 분석 스터디\초,중,고 좌표\학교좌표.csv', encoding='cp949')
# a=pd.read_csv(r'D:\부동산 빅데이터 분석 스터디\초,중,고 좌표\학교좌표.csv', encoding='cp949')

school['geometry']=school.apply(lambda row : Point(row.x, row.y), axis=1)
school_geo=gpd.GeoDataFrame(school, geometry='geometry', crs='epsg:4326')
school_geo=school_geo.to_crs(epsg5181_qgis)

# school_geo.plot()

#%%
from dateutil.parser import parse
import datetime as dt

apart=pd.read_csv(r'D:\부동산 빅데이터 분석 스터디\new\서울특별시 공동주택 아파트 정보.csv', encoding='cp949')
apart['k-사용검사일-사용승인일']=apart['k-사용검사일-사용승인일'].astype(str)

apart=apart.dropna(subset=['k-사용검사일-사용승인일'])

apart=apart[apart['k-사용검사일-사용승인일']!='nan']
apart['k-사용검사일-사용승인일']=[parse(a) for a in apart['k-사용검사일-사용승인일']]

x = dt.datetime.now()

apart['사용연수_days']=x-apart['k-사용검사일-사용승인일']

apart['사용연수']=[int(a.days/365) for a in apart['사용연수_days']]

apart.columns

apart=apart[apart['k-세대타입(분양형태)']!='임대']

apart=apart[['k-아파트명', 'k-단지분류(아파트,주상복합등등)', 'kapt도로명주소',
       '주소(시도)k-apt주소split', '주소(시군구)', '주소(읍면동)', '나머지주소', '주소(도로명)',
       '주소(도로상세주소)', 'k-복도유형', 'k-난방방식', 'k-세대타입(분양형태)', 'k-전체동수', 'k-전체세대수', 
       'k-사용검사일-사용승인일', 'k-연면적', 'k-주거전용면적',
       'k-관리비부과면적', 'k-전용면적별세대현황(60㎡이하)', 'k-전용면적별세대현황(60㎡~85㎡이하)',
       'k-85㎡~135㎡이하', 'k-135㎡초과', '건축면적', '주차대수', '좌표X', '좌표Y', '사용연수']]

apart['geometry']=apart.apply(lambda row : Point(row.좌표X, row.좌표Y), axis=1)

apart_geo=gpd.GeoDataFrame(apart, geometry='geometry', crs='epsg:4326')
apart_geo=apart_geo.to_crs(epsg5181_qgis)

apart_geo=apart_geo.dropna(subset=['좌표X', '좌표Y'])

#%%

elementary=school_geo[school_geo['학교종류명']=='초등학교']
middle=school_geo[school_geo['학교종류명']=='중학교']
high=school_geo[school_geo['학교종류명']=='고등학교']

for i in tqdm(apart_geo.index) :
    for j in range(50, 3000, 50) :
        buf=apart_geo.loc[i, 'geometry'].buffer(j)
        a=pd.DataFrame(elementary.geometry.intersects(buf))
        a=a.astype(str)
        a.columns=['a']
        a=a[a['a']=='True']
        
        if len(a) > 0 :
            break 
        
    apart_geo.loc[i, '초등학교거리']=j
    
    for j in range(50, 3000, 50) :
        buf=apart_geo.loc[i, 'geometry'].buffer(j)
        
        a=pd.DataFrame(middle.geometry.intersects(buf))
        a=a.astype(str)
        a.columns=['a']
        a=a[a['a']=='True']
        
        if len(a) > 0 :
            break 
    
    apart_geo.loc[i, '중학교거리']=j
    
    for j in range(50, 3000, 50) :
        buf=apart_geo.loc[i, 'geometry'].buffer(j)
        
        a=pd.DataFrame(high.geometry.intersects(buf))
        a=a.astype(str)
        a.columns=['a']
        a=a[a['a']=='True']
        
        if len(a) > 0 :
            break 
    
    apart_geo.loc[i, '고등학교거리']=j

apart_geo.to_csv(r'D:\부동산 빅데이터 분석 스터디\초,중,고 좌표\학교까지 거리.csv', encoding='cp949')

#%%

hospital=pd.read_csv(r'D:\부동산 빅데이터 분석 스터디\new\서울특별시 병원 인허가 정보.csv', encoding='cp949')
hospital=hospital[hospital['상세영업상태명']=='영업중']

big_hospital=hospital[hospital['업태구분명']=='종합병원']
big_hospital=big_hospital.dropna(subset=['좌표정보(X)'])
big_hospital=big_hospital.rename(columns={'좌표정보(X)' : 'x', '좌표정보(Y)' : 'y'})
big_hospital['geometry']=big_hospital.apply(lambda row : Point(row.x, row.y), axis=1)

geo_hospital=gpd.GeoDataFrame(big_hospital, geometry='geometry', crs=epsg5181_qgis)

for i in tqdm(apart_geo.index) :
    for j in range(10, 5000, 10) :
        buf=apart_geo.loc[i, 'geometry'].buffer(j)
        a=pd.DataFrame(geo_hospital.geometry.intersects(buf))
        a=a.astype(str)
        a.columns=['a']
        a=a[a['a']=='True']
        
        if len(a) > 0 :
            break 
        
    apart_geo.loc[i, '종합병원거리']=j

#%%

park=pd.read_csv(r'D:\부동산 빅데이터 분석 스터디\new\서울시 주요 공원현황.csv', encoding='cp949')
park=park.rename(columns={'X좌표(WGS84)' : 'x', 'Y좌표(WGS84)' : 'y'})

park['geometry']=park.apply(lambda row : Point(row.x, row.y), axis=1)

geo_park=gpd.GeoDataFrame(park, geometry='geometry', crs='epsg:4326')
geo_park=geo_park.to_crs(epsg5181_qgis)

for i in tqdm(apart_geo.index) :
    for j in range(10, 5000, 10) :
        buf=apart_geo.loc[i, 'geometry'].buffer(j)
        a=pd.DataFrame(geo_park.geometry.intersects(buf))
        a=a.astype(str)
        a.columns=['a']
        a=a[a['a']=='True']
        
        if len(a) > 0 :
            break 
        
    apart_geo.loc[i, '주요 공원 거리']=j

#%%

subway=gpd.GeoDataFrame.from_file(r'D:\부동산 빅데이터 분석 스터디\아파트 찾기 프로젝트 수정\subway.shp', encoding='cp949')
subway2=subway.to_crs(epsg5181_qgis)

for i in tqdm(apart_geo.index) :
    for j in range(10, 5000, 10) :
        buf=apart_geo.loc[i, 'geometry'].buffer(j)
        try :
            a=pd.DataFrame(subway2.geometry.intersects(buf))
            a=a.astype(str)
            a.columns=['a']
            a=a[a['a']=='True']
            
            if len(a) > 0 :
                break 
            
            apart_geo.loc[i, '지하철거리']=j
        
        except :
            break
            apart_geo.loc[i, '지하철거리']=np.nan

apart_geo.to_csv(r'D:\부동산 빅데이터 분석 스터디\아파트 찾기 프로젝트 수정\서울 아파트.csv', encoding='cp949')
#%%
# 세대수, 도로명주소 없는 아파트는 크롤링을 통해 입력.. 진행중

apart_geo=pd.read_csv(r'D:\부동산 빅데이터 분석 스터디\아파트 찾기 프로젝트 수정\서울 아파트.csv', encoding='cp949')
del apart_geo['Unnamed: 0']

#%%
# seoul_area=gpd.GeoDataFrame.from_file(r'C:\Users\user\OneDrive\바탕 화면\부동산 빅데이터 분석 스터디\과제\3주차 수업 과제\geopandas 소방서 띄우기\LARD_ADM_SECT_SGG_11.shp', engine='python', encoding='utf-8')
# seoul_area=seoul_area.to_crs(epsg5181_qgis)

# ax = seoul_area.plot(column="SGG_NM", figsize=(8,8), alpha=0.8)
# geo_park.plot(ax=ax, marker='v', color='blue', label='Park', markersize=100)

# plt.legend()
# plt.show()
