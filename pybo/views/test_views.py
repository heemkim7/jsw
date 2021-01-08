
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import bs4.element
from datetime import datetime
import time
from gensim.summarization.summarizer import summarize
from slacker import Slacker
from urllib.parse import quote_plus
import json


@login_required(login_url='common:login')
def test(request):
    tag_list = []

    kakao_url = "https://dapi.kakao.com/v2/translation/translate?src_lang=en&target_lang=kr&query="
    header = {'Authorization': 'KakaoAK f243bd91b5ce2126687ae268bc33dddf'}
    query = ''

    url = "https://www.google.com/search?q=korea&hl=en&tbs=qdr:h,sbd:1&tbm=nws&sxsrf=ALeKk01WiSVX-lQmK6PlXpZ8AyKz6WkVxQ:1609982845768&source=lnt&sa=X&ved=0ahUKEwig3_a81YjuAhXof94KHctiCW4QpwUIJw&biw=1680&bih=1236&dpr=1"

    soup = get_soup_obj(url)

    # 해당 분야 상위 뉴스 10개 가져오기
    news_list10 = []
    lis10 = soup.find('div', id='rso').find_all('g-card', limit=10)

    for lis in lis10:
        print(lis.a.attrs.get('href'))
        print(lis.find('div', class_='JheGif nDgy9d').get_text())
        query = lis.find('div', class_='JheGif nDgy9d').get_text()
        r = requests.get(kakao_url + query, headers=header)
        dict = json.loads(r.text)
        print(dict['translated_text'][0][0])
        title_ko = dict['translated_text'][0][0]

        print(lis.find('div', class_='Y3v8qd').get_text())
        query = lis.find('div', class_='Y3v8qd').get_text()
        r = requests.get(kakao_url + query, headers=header)
        dict = json.loads(r.text)
        print(dict['translated_text'][0][0])
        desc_ko = dict['translated_text'][0][0]

        print('----------')
        # title : 뉴스 제목, news_url : 뉴스 URL, image_url : 이미지 URL
        news_info = {
            "url": lis.a.attrs.get('href'),
            "title": lis.find('div', class_='JheGif nDgy9d').get_text(),
            "desc": lis.find('div', class_='Y3v8qd').get_text(),
            "title_ko": title_ko,
            "desc_ko": desc_ko
        }
        news_list10.append(news_info)


    print(news_list10)


    # 3번에 걸쳐 각 뉴스의 요약 결과를 전송합니다
    for idx, news_info in enumerate(news_list10):
        slack = Slacker('xoxb-1615709181554-1615920445683-0Jq0kIhfrquKmSz6izJ4okgj')
        slack.chat.post_message('#jsw', '['+str(news_info.get('title_ko'))+']'+'\n'+str(news_info.get('desc_ko'))+'\n'+str(news_info.get('url')))



    context = {'tag_list': tag_list}
    return render(request, 'pybo/upload_taglist.html', context)


# BeautifulSoup 객체 생성
def get_soup_obj(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')

    return soup



# 뉴스의 기본 정보 가져오기
def get_top3_news_info(sec, sid):
    # 임시 이미지
    default_img = "https://search.naver.com/search.naver?where=image&sm=tab_jum&query=naver#"

    # 해당 분야 상위 뉴스 목록 주소
    sec_url = "https://news.naver.com/main/list.nhn?mode=LSD&mid=sec" \
              + "&sid1=" \
              + sid
    #print("section url : ", sec_url)

    # 해당 분야 상위 뉴스 HTML 가져오기
    soup = get_soup_obj(sec_url)

    # 해당 분야 상위 뉴스 3개 가져오기
    news_list3 = []
    lis3 = soup.find('ul', class_='type06_headline').find_all("li", limit=10)
    for li in lis3:
        # title : 뉴스 제목, news_url : 뉴스 URL, image_url : 이미지 URL
        news_info = {
            "title": li.img.attrs.get('alt') if li.img else li.a.text.replace("\n", "").replace("\t", "").replace("\r",
                                                                                                                  ""),
            "date": li.find(class_="date").text,
            "news_url": li.a.attrs.get('href'),
            "image_url": li.img.attrs.get('src') if li.img else default_img
        }
        news_list3.append(news_info)

    return news_list3


# 뉴스의 기본 정보 가져오기
def get_top3_news_info_youtube(sec, sid):
    # 임시 이미지
    default_img = "https://search.naver.com/search.naver?where=image&sm=tab_jum&query=naver#"

    # 해당 분야 상위 뉴스 목록 주소
    sec_url = "https://news.naver.com/main/list.nhn?mode=LSD&mid=sec" \
              + "&sid1=" \
              + sid
    #print("section url : ", sec_url)

    # 해당 분야 상위 뉴스 HTML 가져오기
    soup = get_soup_obj(sec_url)

    # 해당 분야 상위 뉴스 3개 가져오기
    news_list3 = []
    lis3 = soup.find('ul', class_='type06_headline').find_all("li", limit=10)
    for li in lis3:
        # title : 뉴스 제목, news_url : 뉴스 URL, image_url : 이미지 URL
        news_info = {
            "title": li.img.attrs.get('alt') if li.img else li.a.text.replace("\n", "").replace("\t", "").replace("\r",
                                                                                                                  ""),
            "date": li.find(class_="date").text,
            "news_url": li.a.attrs.get('href'),
            "image_url": li.img.attrs.get('src') if li.img else default_img
        }
        news_list3.append(news_info)

    return news_list3


# 뉴스 본문 가져오기
def get_news_contents(url):
    soup = get_soup_obj(url)
    body = soup.find('div', class_="_article_body_contents")

    news_contents = ''
    for content in body:
        if type(content) is bs4.element.NavigableString and len(content) > 50:
            # content.strip() : whitepace 제거 (참고 : https://www.tutorialspoint.com/python3/string_strip.htm)
            # 뉴스 요약을 위하여 '.' 마침표 뒤에 한칸을 띄워 문장을 구분하도록 함
            news_contents += content.strip() + ' '

    return news_contents


# '정치', '경제', '사회' 분야의 상위 3개 뉴스 크롤링
def get_naver_news_top3():
    # 뉴스 결과를 담아낼 dictionary
    news_dic = dict()

    # sections : '정치', '경제', '사회'
    sections = ["home", "eco", "wor", "sci"]
    # section_ids :  URL에 사용될 뉴스  각 부문 ID
    section_ids = ["001", "101", "104", "105"]

    for sec, sid in zip(sections, section_ids):
        # 뉴스의 기본 정보 가져오기
        news_info = get_top3_news_info(sec, sid)
        # print(news_info)
        for news in news_info:
            # 뉴스 본문 가져오기
            news_url = news['news_url']
            news_contents = get_news_contents(news_url)

            # 뉴스 정보를 저장하는 dictionary를 구성
            news['news_contents'] = news_contents

        news_dic[sec] = news_info

    return news_dic



test_flag = True

@login_required(login_url='common:login')
def test_start(request):
    tag_list = []
    print('start')

    global test_flag
    test_flag = True

    #test_run()
    test_run_google()

    context = {'tag_list': tag_list}
    return render(request, 'pybo/upload_taglist.html', context)


@login_required(login_url='common:login')
def test_end(request):
    tag_list = []
    print('end')

    global test_flag
    test_flag = False

    #test_run()
    test_run_google()

    context = {'tag_list': tag_list}
    return render(request, 'pybo/upload_taglist.html', context)




def test_run():
    global test_flag
    # 기존에 보냈던 링크를 담아둘 리스트
    old_links = []
    keyword = ['korea','Korea','KOREA']

    while test_flag:
        #################### 네이버뉴스 크롤링 ####################

        # 함수 호출 - '정치', '경제', '사회' 분야의 상위 3개 뉴스 크롤링
        news_dic = get_naver_news_top3()


        #################### gensim 뉴스요약 ####################

        # 섹션 지정
        my_section = 'wor'
        news_list3 = news_dic[my_section]
        # 뉴스 요약하기
        for news_info in news_list3:
            # 뉴스 본문이 10 문장 이하일 경우 결과가 반환되지 않음.
            # 이때는 요약하지 않고 본문에서 앞 3문장을 사용함.
            try:
                snews_contents = summarize(news_info['news_contents'], word_count=20)
            except:
                snews_contents = None

            if not snews_contents:
                news_sentences = news_info['news_contents'].split('.')

                if len(news_sentences) > 3:
                    snews_contents = '.'.join(news_sentences[:3])
                else:
                    snews_contents = '.'.join(news_sentences)

            news_info['snews_contents'] = snews_contents


        #################### 메시지 보내기 ####################

        # 사용자가 선택한 카테고리를 제목에 넣기 위한 dictionary
        sections_ko = {'eco': '경제', 'wor': '세계', 'sic': 'IT/과학'}

        # 네이버 뉴스 URL
        navernews_url = "https://news.naver.com/main/home.nhn"

        # 추후 각 리스트에 들어갈 내용(content) 만들기
        contents = []

        # 리스트 템플릿 형식 만들기
        template = {
            "object_type": "list",
            "header_title": sections_ko[my_section] + " 분야 상위 뉴스 빅3",
            "header_link": {
                "web_url": navernews_url,
                "mobile_web_url": navernews_url
            },
            "contents": contents,
            "button_title": "네이버 뉴스 바로가기"
        }
        ## 내용 만들기
        # 각 리스트에 들어갈 내용(content) 만들기
        new_links = []
        for news_info in news_list3:
            content = {
                "title": news_info.get('title'),
                "description": "작성일 : " + news_info.get('date'),
                "image_url": news_info.get('image_url'),
                "image_width": 50, "image_height": 50,
                "link": {
                    "web_url": news_info.get('news_url'),
                    "mobile_web_url": news_info.get('news_url')
                }
            }

            for idx in keyword:
                if(news_info.get('title').find(idx) > -1 or news_info.get('news_contents').find(idx) > -1):
                    contents.append(content)
                    if news_info.get('news_url') not in old_links:
                        new_links.append(news_info.get('news_url'))
            new_links = list(set(new_links))

        #print(contents)
        print(str(datetime.now()))
        print('===이전 링크===\n', old_links, '\n')
        print('===보낼 링크===\n', new_links, '\n')
        old_links += new_links.copy()
        old_links = list(set(old_links))


        for link in new_links:
            print(link)
            slack = Slacker('xoxb-1615709181554-1615920445683-0Jq0kIhfrquKmSz6izJ4okgj')
            slack.chat.post_message('#jsw', link)

        # 3번에 걸쳐 각 뉴스의 요약 결과를 전송합니다
        #for idx, news_info in enumerate(news_list3):
            #print('['+news_info.get('title')+']'+'\n'+news_info.get('snews_contents'))
            #slack = Slacker('xoxb-1615709181554-1615920445683-0Jq0kIhfrquKmSz6izJ4okgj')
            #slack.chat.post_message('#jsw', '['+news_info.get('title')+']'+'\n'+news_info.get('snews_contents'))

        time.sleep(10)



def test_run_google():
    global test_flag
    # 기존에 보냈던 링크를 담아둘 리스트
    old_links = []
    kakao_url = "https://dapi.kakao.com/v2/translation/translate?src_lang=en&target_lang=kr&query="
    header = {'Authorization': 'KakaoAK f243bd91b5ce2126687ae268bc33dddf'}
    query = ''
    url = "https://www.google.com/search?q=korea&source=lmns&tbm=nws&bih=1179&biw=1680&hl=en&sa=X&ved=2ahUKEwjsu_nGoYnuAhUIAKYKHaEDDnIQ_AUoA3oECAEQAw"

    while test_flag:
        soup = get_soup_obj(url)

        # 해당 분야 상위 뉴스 10개 가져오기
        news_list10 = []
        lis10 = soup.find('div', id='rso').find_all('g-card', limit=10)

        for lis in lis10:
            #print(lis.a.attrs.get('href'))
            #print(lis.find('div', class_='JheGif nDgy9d').get_text())
            # query = lis.find('div', class_='JheGif nDgy9d').get_text()
            # r = requests.get(kakao_url + query, headers=header)
            # dict = json.loads(r.text)
            # #print(dict['translated_text'][0][0])
            # title_ko = dict


            #print('----------')
            # title : 뉴스 제목, news_url : 뉴스 URL, image_url : 이미지 URL
            news_info = {
                "url": lis.a.attrs.get('href'),
                "title": lis.find('div', class_='JheGif nDgy9d').get_text(),
                "desc": lis.find('div', class_='Y3v8qd').get_text(),
            }

            if news_info not in old_links:
                news_list10.append(news_info)
            news_list10 = list({news_list10['url']: news_list10 for news_list10 in news_list10}.values())



        #print(news_list10)



        #print(contents)
        print(str(datetime.now()))
        print('===이전 링크===\n', old_links, '\n')
        print('===보낼 링크===\n', news_list10, '\n')
        old_links += news_list10.copy()
        old_links = list({old_links['url']: old_links for old_links in old_links}.values())

        # 3번에 걸쳐 각 뉴스의 요약 결과를 전송합니다
        for idx, news_info in enumerate(news_list10):
            slack = Slacker('xoxb-1615709181554-1615920445683-0Jq0kIhfrquKmSz6izJ4okgj')
            slack.chat.post_message('#jsw', '[' + str(news_info.get('title')) + ']' + '\n' + str(news_info.get('url')))

        time.sleep(60)