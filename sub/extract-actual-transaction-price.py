# -*- coding: utf-8 -*-
"""
Created on Sat Apr  3 19:50:41 2021

@author: user
"""

import pandas
import geopandas
import numpy
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import warnings
warnings.filterwarnings(action='ignore') 
import os

# dict_sig은 처음에 비어있으니 예를들어서 '영등포구' 키를 저장. 그리고 해당 아파트의 실거래가가 나올 때 까지 [202103, 202102, 202101...] 이런 식으로 for문을 돌림. 
# 만약 202011에서 실거래가가 나왔다면 dict_sig={'영등포구' : {202103 : xml1, 202102 : xm2, 202101 : xm3, 202012 : xm4, 202011 : xm5}}가 담김
# 이제 다음 아파트에서 for문을 돌리는데 해당 아파트가 영등포구에 속해있다면 dict_sig['영등포구'][202103] 부터 하나씩 for문을 돌리면서 실거래가가 나올때까지 돌림. 
# 그리고 그 아파트가 202102에서 실거래가 나왔다면 for문을 break 하고 다음 아파트로 넘어감.
# 202103, 202102, 202101.... 이렇게 역순으로 내려가면서 해당 아파트 실거래가가 있을때 그 달의 가장 늦은 날짜의 실거래가를 저장하고 for 문을 break 하는 방식으로 해야할 듯

danji_apt=pd.read_csv(r'D:\부동산 빅데이터 분석 스터디\아파트 찾기 프로젝트 수정\서울 아파트.csv', encoding='cp949', sep=',')
del danji_apt['Unnamed: 0']
del danji_apt['geometry']

# 법정동 코드 추가하기

for_pnu=pd.read_csv(r'D:\부동산 빅데이터 분석 스터디\상권 프로젝트 수정\상권 프로젝트\상권 프로젝트\소상공인시장진흥공단_상가(상권)정보_서울.csv', engine='python', encoding='utf-8', sep='|')
for_pnu=for_pnu.drop_duplicates(subset='법정동코드')

bjdcode_list=[]

for i in tqdm(danji_apt.index) :
    for j in for_pnu.index :
        if (danji_apt.loc[i, '주소(시군구)'] == for_pnu.loc[j, '시군구명']) & (danji_apt.loc[i, '주소(읍면동)'] == for_pnu.loc[j, '법정동명']) :
            bjdcode_list.append(str(for_pnu.loc[j, '법정동코드']))
bjd_df=pd.DataFrame(bjdcode_list)
danji_apt.insert(loc=2, column='법정동코드(10자리)', value=bjd_df)


danji_apt_sexy=danji_apt.copy() # 실거래가 조회할때 쓰기 위함
#%%

sexy_poor=danji_apt_sexy.copy()

sexy_poor=sexy_poor.drop_duplicates(subset='법정동코드(10자리)')
sexy_poor['시 코드']=sexy_poor['법정동코드(10자리)'].str[:2]
sexy_poor=sexy_poor.loc[sexy_poor['시 코드']=='11']

poor_count=len(sexy_poor)

sexy_poor2=sexy_poor[['주소(읍면동)', '법정동코드(10자리)']]

# 국토교통부 아파트 실거래가 Api를 이용해서 실거래가 컬럼 추가하기

empty_moong={'가장 최근 실거래가' : [], '거래 금액' : []}
dict_sig={}

# 아파트 검색기 일부 과정을 통해서 danji_apt_geo_final DB를 만들었다는 가정 하에 진행

for moong1, moong2, moong3 in zip(danji_apt_geo_final['법정동 구 코드'], danji_apt_geo_final['건물 이름'], danji_apt_geo_final['PNU']):
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
                if dong==sexy_poor2.loc[i, '주소(읍면동)']:
                    dongcode=str(sexy_poor2.loc[i, '법정동코드(10자리)'])[5:] # xml에서는 법정동코드가 없기 때문에 법정동명과 법정동코드가 있는 파일과 매칭해서 법정동 코드를 가져옴
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
        
        for index, row in price_final.iterrows() :
            empty=empty+row['Year']+'년 '+row['Month']+'월 '+row['Day']+'일 / '+row['Apart']+' '+row['Floor']+ '층 / 전용면적 : ' + row['Area']+ ' m2'
            empty2= front + '억 ' + behind + '만원'
                
        empty_moong['가장 최근 실거래가'].append(empty)
        empty_moong['거래 금액'].append(empty2)
    
    else : # 2020.03부터 한번이라도 거래된적이 없음
        empty_moong['가장 최근 실거래가'].append(f'{moong2} / 1년간 거래 없음')
        empty_moong['거래 금액'].append('')

