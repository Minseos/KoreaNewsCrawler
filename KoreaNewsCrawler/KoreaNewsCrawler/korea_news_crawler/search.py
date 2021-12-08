import requests
from pandas import DataFrame
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os

def search():
  date = str(datetime.now())
  date = date[:date.rfind(":")].replace(" ", "_")
  date = date.replace(":","시") + "분"



  query = input("검색 키워드를 입력하세요 : ")
  news_num = int(input("찾고 싶은 뉴스 기사의 수를 입력하세요 : "))
  query = query.replace(" ", "+")


  news_url = "https://search.naver.com/search.naver?where=news&sm=tab_jum&query={}"

  req = requests.get(news_url.format(query))
  soup = BeautifulSoup(req.text, "html.parser")


  news_dict = {}
  idx = 0
  cur_page = 1

  print()
  print("작성 중...")

  while idx < news_num:
      
      table = soup.find('ul',{'class' : 'list_news'})
      li_list = table.find_all('li', {'id': re.compile('sp_nws.*')})
      area_list = [li.find('div', {'class' : 'news_area'}) for li in li_list]
      a_list = [area.find('a', {'class' : 'news_tit'}) for area in area_list]
      
      for n in a_list[:min(len(a_list), news_num-idx)]:
          news_dict[idx] = {'title' : n.get('title'),
                            'url' : n.get('href') }
          idx += 1

      cur_page += 1

      pages = soup.find('div', {'class' : 'sc_page_inner'})
      next_page_url = [p for p in pages.find_all('a') if p.text == str(cur_page)][0].get('href')
      
      req = requests.get('https://search.naver.com/search.naver' + next_page_url)
      soup = BeautifulSoup(req.text, 'html.parser')

  print("작성 완료!")

  print("데이터프레임 변환")
  news_df = DataFrame(news_dict).T

  folder_path = os.getcwd()
  xlsx_file_name = "네이버뉴스_{}_{}.xlsx".format(query, date)

  news_df.to_excel(xlsx_file_name)

  print("엑셀 저장 완료 | 경로 : {}\\{}".format(folder_path, xlsx_file_name))
  os.startfile(folder_path)