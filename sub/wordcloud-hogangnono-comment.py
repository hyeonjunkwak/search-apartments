# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 22:55:19 2021

@author: user
"""

import sys
sys.version

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import os
import time
import numpy as np
import re
from tqdm import tqdm
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings(action='ignore') 
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

for _ in tqdm(range(125)) : # 최대 500개까지만 띄워서 분석하는게 나을듯
    try :
        sexy=wd.find_element_by_xpath('//*[@id="container"]/div[4]/div[2]/div/div[2]/div[1]/div[2]/div/div[1]/a')
        wd.execute_script("arguments[0].scrollIntoView();", sexy)
        time.sleep(0.5)
        wd.execute_script("arguments[0].click();", sexy)
        time.sleep(0.5)
    
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

# 전처리

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

#%%
# wd.get("http://www.example.com")

# p_element = wd.find_elements_by_tag_name("p")
# print(p_element[1].text)