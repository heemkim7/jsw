
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import bs4.element
from datetime import datetime
import time
from gensim.summarization.summarizer import summarize
from urllib.parse import quote_plus
import json
import os
from PIL import Image, ImageDraw, ImageFont
import random
from ..models import Upload, Keyword
import http.client
import httplib2
import os
import random
import sys
import time
import subprocess

from ..api import slack


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
        slack.chat.post_message('#jsw', '['+str(news_info.get('title_ko'))+']'+'\n'+str(news_info.get('desc_ko'))+'\n'+str(news_info.get('url')))



    context = {'tag_list': tag_list}
    return render(request, 'pybo/upload_keyword_list.html', context)



@login_required(login_url='common:login')
def test2(request):
    tag_list = []


    # wave 파일 사이즈 가져오기
    # import wave
    # import contextlib
    # audiofile = './static/output/1.wav'
    # with contextlib.closing(wave.open(audiofile, 'r')) as f:
    #     frames = f.getnframes()
    #     rate = f.getframerate()
    #     length = frames / float(rate)
        #print(length)
        #print(int(length) * 60)


    from mutagen.mp3 import MP3

    import sys
    import urllib.request
    client_id = "6ahcwqg90m"
    client_secret = "lIFCWuoKMWKqUrLKlmmL4RJdcUN3AkccvCBH5aD9"
    url = "https://naveropenapi.apigw.ntruss.com/voice/v1/tts"
    request_api = urllib.request.Request(url)
    request_api.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
    request_api.add_header("X-NCP-APIGW-API-KEY", client_secret)


    # 파일 라인수 세기
    cnt = 0
    with open('./static/output/script_156_2.txt', 'r', encoding="utf-8") as file:
        while True:
            if file.readline() == '':
                break
            cnt += 1


    # 파일 읽으면서 2라인씩 붙이기
    lineCnt = 1
    lineSum = ''
    with open('./static/output/script_156_2.txt', 'r', encoding="utf-8") as file:
        #print(len(file.readlines()))
        for line in file.readlines():
            line = line.replace('\n', ' ')

            if lineCnt % 2 == 0:
                lineSum += line
                encText = urllib.parse.quote(lineSum)


                # Naver 음성 API 사용 (CSS)
                # data = "speaker=jinho&speed=0&text=" + encText;
                # response = urllib.request.urlopen(request_api, data=data.encode('utf-8'))
                # rescode = response.getcode()
                # if (rescode == 200):
                #     print("TTS mp3 저장")
                #     response_body = response.read()
                #     with open('./static/output/mp3/'+ str(int(lineCnt/2)) + '.mp3', 'wb') as f:
                #         f.write(response_body)
                # else:
                #     print("Error Code:" + rescode)

                # audiofile = './static/output/mp3/('+ str(int(lineCnt/2)) + ').mp3'
                # audio = MP3(audiofile)
                # print(str(int(lineCnt/2)), lineSum, int(audio.info.length * 60))

                lineSum = ''
            else:
                lineSum += line
                if cnt == lineCnt:
                    encText = urllib.parse.quote(lineSum)


                    # Naver 음성 API 사용 (CSS)
                    # data = "speaker=jinho&speed=0&text=" + encText;
                    # response = urllib.request.urlopen(request_api, data=data.encode('utf-8'))
                    # rescode = response.getcode()
                    # if (rescode == 200):
                    #     print("TTS mp3 저장")
                    #     response_body = response.read()
                    #     with open('./static/output/mp3/'+ str(int(lineCnt/2+1)) + '.mp3', 'wb') as f:
                    #         f.write(response_body)
                    # else:
                    #     print("Error Code:" + rescode)

                    # audiofile = './static/output/mp3/(' + str(int(lineCnt / 2 +1)) + ').mp3'
                    # audio = MP3(audiofile)
                    # print(str(int(lineCnt / 2 +1)), lineSum, int(audio.info.length * 60))

            lineCnt += 1




    ####### 키워드 -> 이미지 생성 #########
    keyword = '도쿄올림픽 취소'
    fontname = "./static/font/NanumBarunGothicBold.ttf"
    fontsize = 70
    text = keyword
    colorText = "black"
    colorOutline = "red"
    colorBackground = "white"
    font = ImageFont.truetype(fontname, fontsize)
    width, height = getSize(text, font)
    #print(width, height)
    img = Image.new('RGB', (width + 40, height + 40), colorBackground)
    d = ImageDraw.Draw(img)
    d.text((20, height / 2 - 20), text, fill=colorText, font=font)
    d.rectangle((0, 0, width+20, height + 20))  # , outline=colorOutline)
    img.save('./static/output/mp3/1.png')



    ####### 키워드 -> 이미지 생성 #########
    keyword = '도쿄올림픽 취소'
    fontname = "./static/font/NanumBarunGothicBold.ttf"
    fontsize = 70
    text = keyword
    colorText = "black"
    colorOutline = "red"
    colorBackground = "white"
    font = ImageFont.truetype(fontname, fontsize)
    width, height = getSize(text, font)
    #print(width, height)
    img = Image.new('RGB', (width + 40, height + 40), colorBackground)
    d = ImageDraw.Draw(img)
    d.text((20, height / 2 - 20), text, fill=colorText, font=font)
    d.rectangle((0, 0, width+20, height + 20))  # , outline=colorOutline)
    img.save('./static/output/mp3/1.png')


    ####### 썸네일 자동생성 #########
    Image.open("./youtube/2/thumb_bg.png")
    keyword1 = '중국의 김치공정을 박살낼'
    keyword2 = '확실한 증거가 발견된 상황'
    keyword3 = '한국 잘못 건드린 중국'
    keyword4 = '국제적 망신살만 뻗쳤다'
    target_image = Image.open('./youtube/2/thumb_bg.png')  # 일단 기본배경폼 이미지를 open 합니다.
    fontsFolder = "./static/font/"  # 글자로 쓸 폰트 경로
    selectedFont = ImageFont.truetype(os.path.join(fontsFolder, 'NanumBarunGothicBold.ttf'), 150)  # 폰트경로과 사이즈를 설정해줍니다.
    draw = ImageDraw.Draw(target_image)
    draw.text((20, height / 2 - 20), keyword1, fill = "yellow", font = selectedFont, align = 'center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정

    draw.text((20, height / 2 - 20), keyword2, fill="yellow", font=selectedFont, align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    target_image.save('./static/output/mp3/2.png')  # 편집된 이미지를 저장합니다.







    # 프리미어프로 -> 영상 인코딩하기
    #run_video_encoding()

    # run your program and collect the string output
    cmd = "python upload_video.py --file=\"./youtube/test.mp4\" --title=\"업로드 테스트 타이틀2\" --description=\"디스크립션2\""
    cmd += " --keywords=\"뉴스,지식,한국,중국,일본,미국,아베,스가,시진핑,바이든,문재인\" --category=\"25\" --privacyStatus=\"private\""
    cmd += " --thumbnail=\""+ "./youtube/test.jpg" + "\""
    #out_str = subprocess.check_output(cmd, shell=True)
    #print(out_str)

    # run your program and collect the string output
    cmd = "python upload_thumbnail.py --file=\"./youtube/test.jpg\" --video-id=\"UlFuwJ-CDw8\""
    #out_str = subprocess.check_output(cmd, shell=True)
    #print(out_str)







    # 현재 창 정보 알아오기
    # import ctypes
    # lib = ctypes.windll.LoadLibrary('user32.dll')
    # handle = lib.GetForegroundWindow()  # 활성화된 윈도우의 핸들얻음
    # buffer = ctypes.create_unicode_buffer(255)  # 타이틀을 저장할 버퍼
    # lib.GetWindowTextW(handle, buffer, ctypes.sizeof(buffer))  # 버퍼에 타이틀 저장
    # print(buffer.value)  # 버퍼출력
    # rect = ctypes.wintypes.RECT()
    # ff = ctypes.windll.user32.GetWindowRect(handle, ctypes.pointer(rect))
    # print(rect.left,rect.top,rect.right,rect.bottom)
    # print(ff)



    ################################################################################


    context = {'tag_list': tag_list}
    return render(request, 'pybo/upload_keyword_list.html', context)


def getSize(txt, font):
    """
    Font 사이즈 얻기
    """
    testImg = Image.new('RGB', (1, 1))
    testDraw = ImageDraw.Draw(testImg)
    return testDraw.textsize(txt, font)

def random_pop(data):
    """
    랜덤 데이터 뽑기
    """
    if data.__len__() > 0:
        number = random.choice(data)
        data.remove(number)
        return number
    else:
        return None

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
    return render(request, 'pybo/upload_keyword_list.html', context)


@login_required(login_url='common:login')
def test_end(request):
    tag_list = []
    print('end')

    global test_flag
    test_flag = False

    #test_run()
    test_run_google()

    context = {'tag_list': tag_list}
    return render(request, 'pybo/upload_keyword_list.html', context)




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
            slack.chat.post_message('#jsw', link)

        # 3번에 걸쳐 각 뉴스의 요약 결과를 전송합니다
        #for idx, news_info in enumerate(news_list3):
            #print('['+news_info.get('title')+']'+'\n'+news_info.get('snews_contents'))
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
            slack.chat.post_message('#jsw', '[' + str(news_info.get('title')) + ']' + '\n' + str(news_info.get('url')))

        time.sleep(60)