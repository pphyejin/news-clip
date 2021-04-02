import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import datetime
import schedule

# client = MongoClient('localhost', 27017)
client = MongoClient('mongodb://test:test@13.124.124.45', 27017)
db = client.dbmyproject

def get_hottest_article():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://www.usatoday.com/', headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    articles = soup.select('body > main > div.gnt_rr > div.gnt_m_th > a')

    for i in range(0, 7):
        article = articles[i]
        url = article.get("href")

        if url.startswith("/") is True:

            target_url = f'https://www.usatoday.com{url}'

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

            data = requests.get(target_url, headers=headers)

            soup2 = BeautifulSoup(data.text, 'html.parser')

            contents = soup2.select('body > div.gnt_cw_w > main > article')

            og_desc = soup2.select_one('meta[property="og:description"]')['content']
            # og_desc2 = soup2.find("meta", property="og:description")
            # print(og_desc2["content"] if og_desc2 else "No meta description given")

            for content in contents:
                title = content.select_one('h1').text
                date = content.select_one('div.gnt_ar_dt')['aria-label']

                # 12:58 a.m. ET Jan. 23, 2021 추출해서 형변환해주기.
                date1 = date[date.find(".m") - 7:]
                if date1[0] != "1":
                    date2 = "0" + date1[1:27]
                else:
                    date2 = date1[:27]

                y = date2[-4:]
                m = date2[14:17]
                d = date2[19:21]
                time = date2[:5]
                if date2[6] == "a":
                    a_p = "AM"
                else:
                    a_p = "PM"
                date3 = y + "." + m + "." + d + " " + a_p + " " + time

                date_time_obj = datetime.datetime.strptime(date3, '%Y.%b.%d %p %I:%M')


                # 기사를 겹치지 않고 가지고 오기 위한 유니크 키 생성.
                unique_key = url[-11:-1]

                # 크롤링 해오는 시점의 datetime에서 날짜만 저장하기.
                now = datetime.date.today()

                y = now.strftime("%Y")
                m = now.strftime("%m")
                d = now.strftime("%d")

                a = y + "-" + m + "-" + d
                date_now = datetime.datetime.strptime(a, '%Y-%m-%d')

                # url주소가 네이버뉴스홈이면 korea 아이콘으로 db에 같이 저장하기.
                if target_url[:24] == "https://www.usatoday.com" and og_desc is not None:
                    doc = {
                        'icon': "../static/united-states-of-america.png",
                        'unique_key': unique_key,
                        'url': target_url,
                        'title': title,
                        'desc': og_desc,
                        'date': date3,  # 홈페이지 화면에 보이는 날짜 (스트링 형식)
                        'datetime': date_time_obj,  # 최신 시간순으로 정렬하기 위한 시간
                        'media': 'USA TODAY',
                        'save_datetime': date_now,  # db에 저장되는 순간의 시간 (시분초는 0)
                    }

                    document = db.hottestNews.find_one({"unique_key": unique_key})

                    # # Tutor : document가 없다면 추가하기
                    if document is None:
                        db.hottestNews.insert_one(doc)


# get_hottest_article()

def job():
   get_hottest_article()


def run():
   schedule.every().day.at("08:00").do(job)    # 매일 오전 8시 마다 실행.
   while True:
       schedule.run_pending()


if __name__ == "__main__":
   run()