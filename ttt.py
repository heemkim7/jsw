
from PIL import Image, ImageDraw, ImageFont
import os

def getSize(txt, font):
    """
    Font 사이즈 얻기
    """
    testImg = Image.new('RGB', (1, 1))
    testDraw = ImageDraw.Draw(testImg)
    return testDraw.textsize(txt, font)


if __name__ == '__main__':
    ####### 썸네일 자동생성 #########
    keyword1 = '전세계 백신부족사태 결국'
    keyword2 = '한국에서 해결해 버렸다'
    keyword3 = '획기적 신기술 등장'
    keyword4 = '한국 중소기업이 일냈다'


    width_start = 40
    height_start1 = 40
    height_start2 = 160
    height_start3 = 440
    height_start4 = 560
    font_size = 105
    font_type = 'Recipekorea 레코체 FONT.ttf'

    target_image = Image.open('./youtube/2/thumb_wh.png')  # 일단 기본배경폼 이미지를 open 합니다.
    fontsFolder = "./static/font/"  # 글자로 쓸 폰트 경로
    selectedFont = ImageFont.truetype(os.path.join(fontsFolder, font_type), font_size)  # 폰트경로과 사이즈를 설정해줍니다.
    width, height = getSize(keyword1, selectedFont)
    draw = ImageDraw.Draw(target_image)

    add_image = Image.open('C:\projects\djangobook-master\static\output\mp3/test.jpg')
    add_image = add_image.resize((1280, 720))
    target_image.paste(im=add_image, box=(0, 0))


    width1, height1 = getSize(keyword1, selectedFont)
    width2, height2 = getSize(keyword2, selectedFont)
    width3, height3 = getSize(keyword3, selectedFont)
    width4, height4 = getSize(keyword4, selectedFont)

    width_start1 = (1280 - width1) / 2
    width_start2 = (1280 - width2) / 2
    width_start3 = (1280 - width3) / 2
    width_start4 = (1280 - width4) / 2


    # if width1 > width2:
    #     draw.rectangle((width_start + 20, height_start1 + 10, width1 + 30, height_start1 + 100), fill="black")
    #     draw.rectangle((width_start + 20, height_start2 - 40, width2 + 30, height_start2 + 100), fill="black")
    # else:
    #     draw.rectangle((width_start + 20, height_start1 + 10, width1 + 30, height_start1 + 150), fill="black")
    #     draw.rectangle((width_start + 20, height_start2 + 10, width2 + 30, height_start2 + 100), fill="black")
    #
    # if width3 > width4:
    #     draw.rectangle((width_start + 20, height_start3 + 10, width3 + 30, height_start3 + 100), fill="black")
    #     draw.rectangle((width_start + 20, height_start4 - 40, width4 + 30, height_start4 + 100), fill="black")
    # else:
    #     draw.rectangle((width_start + 20, height_start3 + 10, width3 + 30, height_start3 + 150), fill="black")
    #     draw.rectangle((width_start + 20, height_start4 + 10, width4 + 30, height_start4 + 100), fill="black")
    #
    #
    #
    #
    # draw.text((width_start-5, height_start1-5), keyword1, fill="black", font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    # draw.text((width_start-5, height_start2-5), keyword2, fill="black", font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    # draw.text((width_start-5, height_start3-5), keyword3, fill="black", font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    # draw.text((width_start-5, height_start4-5), keyword4, fill="black", font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    #
    # draw.text((width_start+5, height_start1-5), keyword1, fill="black", font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    # draw.text((width_start+5, height_start2-5), keyword2, fill="black", font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    # draw.text((width_start+5, height_start3-5), keyword3, fill="black", font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    # draw.text((width_start+5, height_start4-5), keyword4, fill="black", font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    #
    # draw.text((width_start-5, height_start1+5), keyword1, fill="black", font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    # draw.text((width_start-5, height_start2+5), keyword2, fill="black", font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    # draw.text((width_start-5, height_start3+5), keyword3, fill="black", font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    # draw.text((width_start-5, height_start4+5), keyword4, fill="black", font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    #
    # draw.text((width_start+5, height_start1+5), keyword1, fill="black", font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    # draw.text((width_start+5, height_start2+5), keyword2, fill="black", font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    # draw.text((width_start+5, height_start3+5), keyword3, fill="black", font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    # draw.text((width_start+5, height_start4+5), keyword4, fill="black", font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    #
    #
    # draw.text((width_start, height_start1), keyword1, fill="yellow", font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    # draw.text((width_start, height_start2), keyword2, fill="yellow", font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    # draw.text((width_start, height_start3), keyword3, fill=(255,255,255), font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    # draw.text((width_start, height_start4), keyword4, fill=(255,255,255), font=selectedFont,
    #           align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정


    if width1 > width2:
        draw.rectangle((width_start1 + 20, height_start1 + 10, width_start1 + width1 - 10, height_start1 + 100), fill="black")
        draw.rectangle((width_start2 + 20, height_start2 - 40, width_start2 + width2 - 10, height_start2 + 100), fill="black")
    else:
        draw.rectangle((width_start1 + 20, height_start1 + 10, width_start1 + width1 - 10, height_start1 + 150), fill="black")
        draw.rectangle((width_start2 + 20, height_start2 + 10, width_start2 + width2 - 10, height_start2 + 100), fill="black")

    if width3 > width4:
        draw.rectangle((width_start3 + 20, height_start3 + 10, width_start3 + width3 - 10, height_start3 + 100), fill="black")
        draw.rectangle((width_start4 + 20, height_start4 - 40, width_start4 + width4 - 10, height_start4 + 100), fill="black")
    else:
        draw.rectangle((width_start3 + 20, height_start3 + 10, width_start3 + width3 - 10, height_start3 + 150), fill="black")
        draw.rectangle((width_start4 + 20, height_start4 + 10, width_start4 + width4 - 10, height_start4 + 100), fill="black")




    draw.text((width_start1-5, height_start1-5), keyword1, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start2-5, height_start2-5), keyword2, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start3-5, height_start3-5), keyword3, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start4-5, height_start4-5), keyword4, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정

    draw.text((width_start1+5, height_start1-5), keyword1, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start2+5, height_start2-5), keyword2, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start3+5, height_start3-5), keyword3, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start4+5, height_start4-5), keyword4, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정

    draw.text((width_start1-5, height_start1+5), keyword1, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start2-5, height_start2+5), keyword2, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start3-5, height_start3+5), keyword3, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start4-5, height_start4+5), keyword4, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정

    draw.text((width_start1+5, height_start1+5), keyword1, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start2+5, height_start2+5), keyword2, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start3+5, height_start3+5), keyword3, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start4+5, height_start4+5), keyword4, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정


    draw.text((width_start1, height_start1), keyword1, fill="yellow", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start2, height_start2), keyword2, fill="yellow", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start3, height_start3), keyword3, fill=(255,255,255), font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start4, height_start4), keyword4, fill=(255,255,255), font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정


    target_image.save('./static/output/mp3/2.png')  # 편집된 이미지를 저장합니다.






    # audio_voice API 호출해 다운로드 받아서 각 mp3 시간 구하기
    from mutagen.mp3 import MP3

    from urllib import parse
    from urllib.request import Request, urlopen
    import urllib

    # ccs 키
    #client_id = "6ahcwqg90m"
    #client_secret = "lIFCWuoKMWKqUrLKlmmL4RJdcUN3AkccvCBH5aD9"
    #url = "https://naveropenapi.apigw.ntruss.com/voice/v1/tts"

    # clova voice
    client_id = "milwxmfzvd"
    client_secret = "4chTIlsKvFZdxBMcxAh18rNudMJQBSC86hpDfMOQ"
    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
    request_api = urllib.request.Request(url)
    request_api.add_header("X-NCP-APIGW-API-KEY-ID", client_id)
    request_api.add_header("X-NCP-APIGW-API-KEY", client_secret)

    lineSum = '또 최소 주사잔량과 안전 보호가드등과 관련해 국내 기술특허 및 디자인 특허를 출원하고 미국과 EU 등 국제특허 출원도 진행하고 있습니다.'
    encText = urllib.parse.quote(lineSum)


    # Naver 음성 API 사용 (CSS)
    # speaker = 'nsinu'
    # speed = -1
    # pitch = 0
    # data = "speaker=" + speaker + "&speed=" + str(speed) + "&pitch=" + str(pitch) + "&text=" + encText;
    # response = urllib.request.urlopen(request_api, data=data.encode('utf-8'))
    # rescode = response.getcode()
    # if (rescode == 200):
    #     print("TTS mp3 저장")
    #     response_body = response.read()
    #     with open('./static/output/mp3/voice_' + speaker + '_' + str(speed) + '_' + str(pitch) + '.mp3', 'wb') as f:
    #         f.write(response_body)
    # else:
    #     print("Error Code:" + rescode)

    # from slacker import Slacker
    # slack = Slacker('xoxb-1615709181554-1615920445683-4jYsPvJKhjfppAdWAJB1Qwq0')
    # slack.chat.post_message('#jsw', "test")


    filepath = './youtube/test.mp4'
    #
    # import subprocess
    # cmd = [
    #     'python',
    #     'upload_video_sst.py',
    #     "--file=" + filepath,
    #     "--title=" + "Test2",
    #     "--description=본 채널은 연합뉴스 콘텐츠 이용계약을 맺었으며, 연합뉴스는 본 채널의 편집방향과 무관합니다.\r\n저작권자(C)연합뉴스",
    #     "--keywords=뉴스,한국,중국,일본,미국,잡식,문재인,아베,스가,시진핑,바이든",
    #     "--category=25",
    #     "--privacyStatus=private"
    # ]
    # out_str = subprocess.Popen(cmd, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True,
    #                            creationflags=subprocess.DETACHED_PROCESS)
    # print(out_str)

    filepath = './youtube/2/intro.mp4'
    import subprocess
    # run your program and collect the string output
    cmd = [
        'python',
        'upload_video_sst.py',
        "--file=" + filepath,
        "--title=" + "test3",
        "--description=시사통입니다.",
        "--keywords=뉴스,한국,중국,일본,미국,잡식,문재인,아베,스가,시진핑,바이든",
        "--category=25",
        "--privacyStatus=private"
    ]
    # out_str = subprocess.Popen(cmd, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True,
    #                            creationflags=subprocess.DETACHED_PROCESS)

    out_str = subprocess.check_output(cmd, shell=True)
    print(out_str)