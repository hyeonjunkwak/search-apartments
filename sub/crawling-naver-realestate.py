# -*- coding: utf-8 -*-
"""
Created on Sun Apr 11 22:37:57 2021

@author: user
"""
# 네이버 부동산 매물 크롤링

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import os
import time
import re
import matplotlib.pyplot as plt
import seaborn as sns

os.chdir(r'C:\Users\user\OneDrive\바탕 화면')

wd=webdriver.Chrome('chromedriver.exe')
wd.maximize_window()
wd.implicitly_wait(3)

url='https://new.land.naver.com/complexes?ms=37.462278,126.810925,17&a=APT:ABYG:JGC&e=RETAIL'

wd.get(url)
wd.implicitly_wait(3)

# keyword=input('검색하려는 아파트를 입력하세요 : ')
# 검색 결과 두개 나오는 아파트 필터링 거치기, try except로 하면 될듯
keyword='헬리오시티'

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
