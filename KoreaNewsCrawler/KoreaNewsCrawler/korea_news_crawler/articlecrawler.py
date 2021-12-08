#!/usr/bin/env python
# -*- coding: utf-8, euc-kr -*-


#사용 모듈
from time import sleep
from bs4 import BeautifulSoup
from multiprocessing import Process
from korea_news_crawler.exceptions import *
from korea_news_crawler.articleparser import ArticleParser
from korea_news_crawler.writer import Writer
import os
import platform
import calendar
import requests
import re


#크롤러 클래스
class ArticleCrawler(object):
    #생성자 역할 함수
    #Category와 date등 주요 변수들 생성
    def __init__(self):
        self.categories = {'정치': 100, '경제': 101, '사회': 102, '생활문화': 103, '세계': 104, 'IT과학': 105, 
                            '오피니언': 110, '청와대':264, '국회/정당':265, '북한':268, '행정':266
                           , '국방/외교':267, '정치일반':269, '금융':259, '증권':258, '산업/재계':261, '중기/벤처':771,
                           '부동산':260, '글로벌 경제':262, '생활경제':310, '경제 일반':263, '사건사고':249,'교육':250,
                           '노동':251,'언론':254, '식품/의료':255, '지역':256, '인물': 276, '사회 일반':257, '건강정보':241,
                           '자동차/시승기':239,'도로교통':240, '여행/레저':237, '음식/맛집':238, '패션/뷰티':376, '공연/전시':242,
                           '책':243, '종교':244, '날씨':248, '생활문화 일반':245, '아시아/호주':231, '미국/중남미':232, '유럽':233,
                           '중동/아프리카':234, '세계 일반':322, '모바일':731, '인터넷/SNS':226, '통신/뉴미디어':227, 'IT 일반':230,
                           '보안/해킹':732, '컴퓨터':283, '게임/리뷰':229, '과학 일반':228}
        self.selected_categories = []
        self.date = {'start_year': 0, 'start_month': 0, 'start_date':0, 'end_year': 0, 'end_month': 0, 'end_date': 0}
        self.user_operating_system = str(platform.system())

    #Category 설정 함수
    def set_category(self, *args):
        for key in args:
            if self.categories.get(key) is None:
                raise InvalidCategory(key)
        self.selected_categories = args

    #크롤링할 기사 날짜 설정
    def set_date_range(self, start_year, start_month, start_date, end_year, end_month, end_date):
        args = [start_year, start_month, start_date, end_year, end_month, end_date]
        if start_year > end_year:
            raise InvalidYear(start_year, end_year)
        if start_month < 1 or start_month > 12:
            raise InvalidMonth(start_month)
        if end_month < 1 or end_month > 12:
            raise InvalidMonth(end_month)
        if start_date < 1 or start_date > 32:
            raise InvalidDate(start_date)
        if end_date < 1 or end_date > 32:
            raise InvalidDate(end_date)
        if start_year == end_year and start_month > end_month:
            raise OverbalanceMonth(start_month, end_month)
        if start_year == end_year and start_date > end_date:
            raise OverbalanceMonth(start_date, end_date)
        for key, date in zip(self.date, args):
            self.date[key] = date
        print(self.date)

    #url 설정 함수
    @staticmethod
    def make_news_page_url(category_url, start_year, end_year, start_month, end_month, start_date, end_date):
        made_urls = []
        #전달받은 기간동안 수행
        target_start_month = start_month
        target_end_month = end_month
        for year in range(start_year, end_year + 1):
            if start_year == end_year:
                target_start_month = start_month
                target_end_month = end_month
            else:
                if year == start_year:
                    target_start_month = start_month
                    target_end_month = 12
                elif year == end_year:
                    target_start_month = 1
                    target_end_month = end_month
                else:
                    target_start_month = 1
                    target_end_month = 12
            
            for month in range(target_start_month, target_end_month + 1):
                if target_start_month == target_end_month:
                    for month_day in range(1,  end_date + 1):
                        if len(str(month)) == 1:
                            month = "0" + str(month)
                        if len(str(month_day)) == 1:
                            month_day = "0" + str(month_day)
                else:
                    for month_day in range(1, calendar.monthrange(year, month)[1] + 1):
                        if len(str(month)) == 1:
                            month = "0" + str(month)
                        if len(str(month_day)) == 1:
                            month_day = "0" + str(month_day)
                        
                # 날짜별로 Page Url 생성
                url = category_url + str(year) + str(month) + str(month_day)
                # 전체 페이지 설정(Redirect)
                totalpage = ArticleParser.find_news_totalpage(url + "&page=10000")
                print(totalpage)
                for page in range(1, totalpage + 1):
                    made_urls.append(url + "&page=" + str(page))
                    
        return made_urls

    #data를 받아오는 함수
    @staticmethod
    def get_url_data(url, max_tries=5):
        remaining_tries = int(max_tries)
        headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.90 Safari/537.36'}
        while remaining_tries > 0:
            try:
                return requests.get(url,headers=headers)
            except requests.exceptions:
                sleep(1)
            remaining_tries = remaining_tries - 1
        raise ResponseTimeout()

    #crawling 함수
    def crawling(self, category_name):
        # Multi Process PID
        print(category_name + " PID: " + str(os.getpid()))    

        writer = Writer(category_name=category_name, date=self.date)

        # 기사 URL 형식
        url = "http://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=" + str(self.categories.get(category_name)) + "&date="

        # start_year년 start_month월 start_date일 ~ end_year의 end_month, end_date 날짜까지 기사를 수집합니다.
        target_urls = self.make_news_page_url(url, self.date['start_year'], self.date['end_year'], 
                    self.date['start_month'], self.date['end_month'], self.date['start_date'], self.date['end_date'] )
        
        print(category_name + " URL이 생성되었습니다.")
        print("크롤러를 시작합니다.")

        for URL in target_urls:

            regex = re.compile("date=(\d+)")
            news_date = regex.findall(URL)[0]

            request = self.get_url_data(URL)
            document = BeautifulSoup(request.content, 'html.parser')

            # 각 페이지에 있는 기사들 가져오기
            temp_post = document.select('.newsflash_body .type06_headline li dl')
            temp_post.extend(document.select('.newsflash_body .type06 li dl'))
            
            # 각 페이지에 있는 기사들의 url 저장
            post = []
            for line in temp_post:
                post.append(line.a.get('href')) # 해당되는 page에서 모든 기사들의 URL을 post 리스트에 넣음
            del temp_post

            for content_url in post:  # 기사 URL
                # 크롤링 대기 시간
                sleep(0.01)
                
                # 기사 HTML 가져옴
                request_content = self.get_url_data(content_url)
                try:
                    document_content = BeautifulSoup(request_content.content, 'html.parser')
                except:
                    continue

                try:
                    # 기사 제목 가져옴
                    tag_headline = document_content.find_all('h3', {'id': 'articleTitle'}, {'class': 'tts_head'})
                    text_headline = ''  # 뉴스 기사 제목 초기화
                    text_headline = text_headline + ArticleParser.clear_headline(str(tag_headline[0].find_all(text=True)))
                    if not text_headline:  # 공백일 경우 기사 제외 처리
                        continue

                    # 기사 본문 가져옴
                    tag_content = document_content.find_all('div', {'id': 'articleBodyContents'})
                    text_sentence = ''  # 뉴스 기사 본문 초기화
                    text_sentence = text_sentence + ArticleParser.clear_content(str(tag_content[0].find_all(text=True)))
                    if not text_sentence:  # 공백일 경우 기사 제외 처리
                        continue

                    # 기사 언론사 가져옴
                    tag_company = document_content.find_all('meta', {'property': 'me2:category1'})
                    text_company = ''  # 언론사 초기화
                    text_company = text_company + str(tag_company[0].get('content'))
                    if not text_company:  # 공백일 경우 기사 제외 처리
                        continue
                        
                    # CSV 작성
                    wcsv = writer.get_writer_csv()
                    wcsv.writerow([news_date, category_name, text_company, text_headline, text_sentence, content_url])
                    
                    print('작성 중..')

                    del text_company, text_sentence, text_headline
                    del tag_company 
                    del tag_content, tag_headline
                    del request_content, document_content
                except Exception as ex:
                    del request_content, document_content
                    pass
        print('작성 완료!')
        writer.close()

    # crawling 시작 함수
    def start(self):
        # MultiProcess crawling 시작
        for category_name in self.selected_categories:
            proc = Process(target=self.crawling, args=(category_name,))
            proc.start()
