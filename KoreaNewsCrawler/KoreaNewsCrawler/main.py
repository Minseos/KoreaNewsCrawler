from korea_news_crawler.articlecrawler import ArticleCrawler
from korea_news_crawler.search import search


if __name__ == "__main__":
    answer = input("(키워드, 검색) 중 원하는 크롤링 방법을 입력하세요 : ")
    if answer == "검색" :{
        search()
    }
    elif answer == "키워드":
        Crawler = ArticleCrawler()
        print("정치(청와대, 국회/정당, 북한, 행정, 국방/외교, 정치일반")
        print("경제(금융, 증권, 산업/재계, 중기/벤처, 부동산, 글로벌 경제, 생활경제, 경제 일반")
        print("사회(사건사고, 교육, 노동, 언론, 환경, 인권/복지, 식품/의료, 지역, 인물, 사회 일반")
        print("생활문화(건강정보, 자동차/시승기, 도로교통, 여행/레저, 음식/맛집, 패션/뷰티, 공연/전시, 책, 종교, 날씨, 생활문화 일반")
        print("세계(아시아/호주, 미국/중남미, 유럽, 중동/아프리카, 세계 일반")
        print("IT과학(모바일, 인터넷/SNS, 통신/뉴미디어, IT 일반, 보안/해킹, 컴퓨터, 게임/리뷰, 과학 일반")
        key = input("원하는 키워드를 입력해주세요 : ")
        Crawler.set_category(key)  # 정치, 경제, 생활문화, IT과학, 사회, 세계 카테고리 사용 가능
        s_year = int(input("시작 연도를 입력해주세요 : "))
        s_month = int(input("시작 달을 입력해주세요 : "))
        s_date = int(input("시작 날짜를 입력해주세요 : "))
        e_year = int(input("마지막 연도를 입력해주세요 : "))
        e_month = int(input("마지막 달을 입력해주세요 : "))
        e_date = int(input("마지막 날짜 입력해주세요 : "))
        Crawler.set_date_range(s_year, s_month, s_date, e_year, e_month, e_date)
        Crawler.start()
    else:
        print("다시 입력해주세요")
    


