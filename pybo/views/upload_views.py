from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
import requests
import json
import datetime
import mimetypes
import urllib
import os
import zipfile
import sys
import shutil
import random
from bs4 import BeautifulSoup as bs
from urllib import parse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import quote_plus
from PIL import Image, ImageDraw, ImageFont
from threading import Thread

from ..forms import QuestionForm
from ..models import Question


@login_required(login_url='common:login')
def editor(request):
    """
    pybo 질문등록
    """
    # if request.method == 'POST':
    #     form = QuestionForm(request.POST)
    #     if form.is_valid():
    #         question = form.save(commit=False)
    #         question.author = request.user  # 추가한 속성 author 적용
    #         question.create_date = timezone.now()
    #         question.save()
    #         return redirect('pybo:index')
    # else:
    #     form = QuestionForm()

    qid = request.POST.get('qid', '')
    print('qid : ' + qid)
    keywords = ''

    isFile = os.path.isfile('./static/output/' + 'keyword_'+ qid +'.txt')

    if isFile is True:
        with open('./static/output/' + 'keyword_'+ qid +'.txt', "r", encoding="utf8") as f:
            for line in f.readlines():
                keywords += line

    print('keywords : ' + keywords)

    context = {'qid': request.POST.get('qid', ''),
               'subject': request.POST.get('subject', ''),
               'content': request.POST.get('content', ''),
               'keyword': keywords}
    #print(context)
    return render(request, 'pybo/editor_form.html', context)


@login_required(login_url='common:login')
def editor_create(request):
    """
    pybo 질문등록
    """
    question_id = request.POST.get('qid', '')
    print(question_id)


    if question_id == '':
        # create
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user  # 추가한 속성 author 적용
            question.create_date = timezone.now()
            question.save()
            context = {'status': 'create', 'qid': question.id }
            return HttpResponse(json.dumps(context), content_type="application/json")
    else:
        # modify
        question = get_object_or_404(Question, pk=question_id)
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            question.modify_date = timezone.now()  # 수정일시 저장
            question.save()
            context = {'status': 'modify', 'qid': question.id}
            return HttpResponse(json.dumps(context), content_type="application/json")



def editor_modify_download_true(question_id):
    """
    pybo 다운로드 완료
    """
    question = get_object_or_404(Question, pk=question_id)
    print(question.create_date)
    question.download_flag = '1'
    question.save()
    return redirect('pybo:index')

def editor_modify_download_false(question_id):
    """
    pybo 다운로드 완료
    """
    question = get_object_or_404(Question, pk=question_id)
    print(question.create_date)
    question.download_flag = '0'
    question.save()
    return redirect('pybo:index')



@login_required(login_url='common:login')
def editor_convert(request):
    """
    스크립트 변환
    """
    content = request.POST.get('content', '없음')  # 페이지
    question_id = request.POST.get('qid', '')
    #print("content : ")
    #print(content)
    #print("qid : ")
    #print(question_id)
    context = {'like_count': 1,
               'message': 2,
               'nickname': 3}

    output2 = ''
    fw = open('./static/output/script_'+question_id+'.txt', 'w', encoding="utf-8")


    lineCnt = 0
    charCnt = 0
    lineStr = ""
    for line in str(content).split('\n'):
        #line = line.strip()
        line = line + '\n'
        line = line.replace("\u00A0", " ")
        #print("line : " + line)
        if line.find('{') > -1 and line.find('}') > -1:
            print(str(lineCnt/2))
            continue

        if line.find('[') > -1 and line.find(']') > -1:
            continue

        if line.find('http') > -1:
            continue

        word = line.split(' ')
        for i in word:
            if i == "":
                continue

            charCnt += i.__len__()
            #print("charCnt : " + str(charCnt))

            if i.find("\n") > -1:
                lineStr += i
                fw.write(lineStr)
                output2 += i
                lineStr = ""
                lineCnt = lineCnt + 1
                charCnt = 0
            elif i.find("/") > -1:
                i = i.replace('/', '')
                lineStr += i
                #print(lineCnt, lineStr, end="\n")
                fw.write(lineStr + "\n")
                output2 += i + "\n"
                lineStr = ""
                lineCnt = lineCnt + 1
                charCnt = 0
            elif charCnt > 20:
                lineStr += i
                #print(lineCnt, lineStr, end="\n")
                fw.write(lineStr + "\n")
                output2 += i + "\n"
                lineStr = ""
                lineCnt = lineCnt + 1
                charCnt = 0
            elif i[i.__len__() - 1] == ".":
                lineStr += i
                #print(lineCnt, lineStr, end="\n")
                fw.write(lineStr + "\n")
                output2 += i + "\n"
                lineStr = ""
                lineCnt = lineCnt + 1
                charCnt = 0
            else:
                lineStr += i + " "
                output2 += i + " "

    # line_cnt = 0
    # for line in str(content).split('\n'):
    #     line_cnt += 1
    #
    # lineCnt = 0
    # charCnt = 0
    # lineStr = ""
    # for line in str(content).split('\n'):
    #     if line.find('{') > -1 and line.find('}') > -1:
    #         continue
    #
    #     if line.find('[') > -1 and line.find(']') > -1:
    #         continue
    #
    #     if line.find('http') > -1:
    #         continue
    #
    #     word = line.split(' ')
    #     for i in word:
    #         if i == "":
    #             continue
    #
    #         charCnt += i.__len__()
    #
    #         if i.find("/") > -1:
    #             i = i.replace('/', '')
    #             lineStr += i
    #             print(lineCnt, lineStr, end="\n")
    #             fw.write(lineStr + "\n")
    #             lineStr = ""
    #             lineCnt = lineCnt + 1
    #             charCnt = 0
    #             continue
    #         elif charCnt > 20:
    #             lineStr += i
    #             print(lineCnt, lineStr, end="\n")
    #             fw.write(lineStr + "\n")
    #             lineStr = ""
    #             lineCnt = lineCnt + 1
    #             charCnt = 0
    #         elif i[i.__len__() - 1] == ".":
    #             lineStr += i
    #             print(lineCnt, lineStr, end="\n")
    #             fw.write(lineStr + "\n")
    #             lineStr = ""
    #             lineCnt = lineCnt + 1
    #             charCnt = 0
    #         else:
    #             lineStr += i + " "


    fw.close()

    output = ''
    with open('./static/output/script_'+question_id+'.txt', 'r', encoding="utf-8") as file:
        for line in file.readlines():
            output += line

    #print("output2 : " + output2)
    return HttpResponse(json.dumps(output2), content_type="application/json")



@login_required(login_url='common:login')
def editor_subtitle(request):
    """
    스크립트 자막 xml로 만들기
    """

    line_no = request.GET.get('line', '')
    question_id = request.GET.get('qid', '')
    print(line_no)
    print(question_id)

    lineCnt = 0
    with open('./static/output/script_'+question_id+'.txt', 'r', encoding="utf-8") as file:
        for line in file.readlines():
            line = line.replace('\n', '')
            lineCnt += 1

    now = datetime.datetime.now()
    time_for_text = 600

    ## line 1 ##
    str1 = "<?xml version=\"1.0\" encoding=\"utf-8\"?><xmeml version=\"5\">  <sequence id=\"video\">    <name>"
    name = "자막_layer1_" + now.strftime('%Y%m%d')
    str3 = "</name>    <duration>"
    time = str(int(lineCnt) / 2 * time_for_text)
    str5 = "</duration>    <rate>      <timebase>60</timebase>      <ntsc>false</ntsc>    </rate>    <media>      <video>        <format>          <samplecharacteristics>            <width>1920</width>            <height>1080</height>            <anamorphic>false</anamorphic>            <pixelaspectratio>square</pixelaspectratio>            <fielddominance>none</fielddominance>          </samplecharacteristics>        </format>        <track>"
    result = str1 + name + str3 + time + str5

    ## line 2 ##
    str1_2 = "<?xml version=\"1.0\" encoding=\"utf-8\"?><xmeml version=\"5\">  <sequence id=\"video\">    <name>"
    name_2 = "자막_layer2_" + now.strftime('%Y%m%d')
    str3_2 = "</name>    <duration>"
    time_2 = str(int(lineCnt) / 2 * time_for_text)
    str5_2 = "</duration>    <rate>      <timebase>60</timebase>      <ntsc>false</ntsc>    </rate>    <media>      <video>        <format>          <samplecharacteristics>            <width>1920</width>            <height>1080</height>            <anamorphic>false</anamorphic>            <pixelaspectratio>square</pixelaspectratio>            <fielddominance>none</fielddominance>          </samplecharacteristics>        </format>        <track>"
    result_2 = str1_2 + name_2 + str3_2 + time_2 + str5_2

    ## 반복 ##

    lineCnt = 0
    timeCnt = 0
    with open('./static/output/script_'+question_id+'.txt', 'r', encoding="utf-8") as file:
        for line in file.readlines():
            line = line.replace('\n', '')

            if lineCnt % 2 == 0:
                str6 = "<generatoritem id=\"Outline Text1\">            <name>Outline Text</name>            <rate>              <timebase>60</timebase>              <ntsc>false</ntsc>            </rate>            <start>"
                start_time = str(timeCnt)
                str8 = "</start>            <end>"
                end_time = str(timeCnt + time_for_text)
                str10 = "</end>            <in>"
                # start_time
                str12 = "</in>            <out>"
                # end_time
                str14 = "</out>            <enabled>true</enabled>            <anamorphic>false</anamorphic>            <alphatype>black</alphatype>            <masterclipid>Outline Text1</masterclipid>            <effect>              <name>Outline Text</name>              <effectid>Outline Text</effectid>              <effectcategory>Text</effectcategory>              <effecttype>generator</effecttype>              <mediatype>video</mediatype>              <parameter>                <parameterid>part1</parameterid>                <name>Text Settings</name>                <value/>              </parameter>              <parameter>                <parameterid>str</parameterid>                <name>Text</name>                <value>"
                text = line
                str16 = "</value>              </parameter>              <parameter>                <parameterid>font</parameterid>                <name>Font</name>                <value>BMDoHyeon</value>              </parameter>              <parameter>                <parameterid>style</parameterid>                <name>Style</name>                <valuemin>1</valuemin>                <valuemax>1</valuemax>                <valuelist>                  <valueentry>                    <name>Regular</name>                    <value>1</value>                  </valueentry>                </valuelist>                <value>1</value>              </parameter>              <parameter>                <parameterid>align</parameterid>                <name>Alignment</name>                <valuemin>1</valuemin>                <valuemax>3</valuemax>                <valuelist>                  <valueentry>                    <name>Left</name>                    <value>1</value>                  </valueentry>                  <valueentry>                    <name>Center</name>                    <value>2</value>                  </valueentry>                  <valueentry>                    <name>Right</name>                    <value>3</value>                  </valueentry>                </valuelist>                <value>2</value>              </parameter>              <parameter>                <parameterid>size</parameterid>                <name>Size</name>                <valuemin>0</valuemin>                <valuemax>200</valuemax>                <value>25</value>              </parameter>              <parameter>                <parameterid>track</parameterid>                <name>Tracking</name>                <valuemin>0</valuemin>                <valuemax>100</valuemax>                <value>1</value>              </parameter>              <parameter>                <parameterid>lead</parameterid>                <name>Leading</name>                <valuemin>-100</valuemin>                <valuemax>100</valuemax>                <value>0</value>              </parameter>              <parameter>                <parameterid>aspect</parameterid>                <name>Aspect</name>                <valuemin>0</valuemin>                <valuemax>4</valuemax>                <value>1</value>              </parameter>              <parameter>                <parameterid>linewidth</parameterid>                <name>Line Width</name>                <valuemin>0</valuemin>                <valuemax>200</valuemax>                <value>2</value>              </parameter>              <parameter>                <parameterid>linesoft</parameterid>                <name>Line Softness</name>                <valuemin>0</valuemin>                <valuemax>100</valuemax>                <value>5</value>              </parameter>              <parameter>                <parameterid>textopacity</parameterid>                <name>Text Opacity</name>                <valuemin>0</valuemin>                <valuemax>100</valuemax>                <value>100</value>              </parameter>              <parameter>                <parameterid>center</parameterid>                <name>Center</name>                <value>                  <horiz>0.058</horiz>                  <vert>0.351</vert>                </value>              </parameter>              <parameter>                <parameterid>textcolor</parameterid>                <name>Text Color</name>                <value>                  <alpha>255</alpha>                  <red>0</red>                  <green>0</green>                  <blue>0</blue>                </value>              </parameter>              <parameter>                <parameterid>supertext</parameterid>                <name>Text Graphic</name>              </parameter>              <parameter>                <parameterid>superline</parameterid>                <name>Line Graphic</name>              </parameter>              <parameter>                <parameterid>part2</parameterid>                <name>Background Settings</name>                <value/>              </parameter>              <parameter>                <parameterid>xscale</parameterid>                <name>Horizontal Size</name>                <valuemin>0</valuemin>                <valuemax>200</valuemax>                <value>0</value>              </parameter>              <parameter>                <parameterid>yscale</parameterid>                <name>Vertical Size</name>                <valuemin>0</valuemin>                <valuemax>200</valuemax>                <value>0</value>              </parameter>              <parameter>                <parameterid>xoffset</parameterid>                <name>Horizontal Offset</name>                <valuemin>-100</valuemin>                <valuemax>100</valuemax>                <value>0</value>              </parameter>              <parameter>                <parameterid>yoffset</parameterid>                <name>Vertical Offset</name>                <valuemin>-100</valuemin>                <valuemax>100</valuemax>                <value>0</value>              </parameter>              <parameter>                <parameterid>backsoft</parameterid>                <name>Back Soft</name>                <valuemin>0</valuemin>                <valuemax>100</valuemax>                <value>0</value>              </parameter>              <parameter>                <parameterid>backopacity</parameterid>                <name>Back Opacity</name>                <valuemin>0</valuemin>                <valuemax>100</valuemax>                <value>50</value>              </parameter>              <parameter>                <parameterid>backcolor</parameterid>                <name>Back Color</name>                <value>                  <alpha>255</alpha>                  <red>255</red>                  <green>255</green>                  <blue>255</blue>                </value>              </parameter>              <parameter>                <parameterid>superback</parameterid>                <name>Back Graphic</name>              </parameter>              <parameter>                <parameterid>crop</parameterid>                <name>Crop</name>                <value>false</value>              </parameter>              <parameter>                <parameterid>autokern</parameterid>                <name>Auto Kerning</name>                <value>true</value>              </parameter>            </effect>            <sourcetrack>              <mediatype>video</mediatype> <trackindex>1</trackindex>            </sourcetrack>          </generatoritem>"

                result += str6 + start_time + str8 + end_time + str10 + start_time + str12 + end_time + str14 + text + str16
            else:
                str6_2 = "<generatoritem id=\"Outline Text1\">            <name>Outline Text</name>            <rate>              <timebase>60</timebase>              <ntsc>false</ntsc>            </rate>            <start>"
                start_time_2 = str(timeCnt)
                str8_2 = "</start>            <end>"
                end_time_2 = str(timeCnt + time_for_text)
                str10_2 = "</end>            <in>"
                # start_time
                str12_2 = "</in>            <out>"
                # end_time
                str14_2 = "</out>            <enabled>true</enabled>            <anamorphic>false</anamorphic>            <alphatype>black</alphatype>            <masterclipid>Outline Text1</masterclipid>            <effect>              <name>Outline Text</name>              <effectid>Outline Text</effectid>              <effectcategory>Text</effectcategory>              <effecttype>generator</effecttype>              <mediatype>video</mediatype>              <parameter>                <parameterid>part1</parameterid>                <name>Text Settings</name>                <value/>              </parameter>              <parameter>                <parameterid>str</parameterid>                <name>Text</name>                <value>"
                text_2 = line
                str16_2 = "</value>              </parameter>              <parameter>                <parameterid>font</parameterid>                <name>Font</name>                <value>BMDoHyeon</value>              </parameter>              <parameter>                <parameterid>style</parameterid>                <name>Style</name>                <valuemin>1</valuemin>                <valuemax>1</valuemax>                <valuelist>                  <valueentry>                    <name>Regular</name>                    <value>1</value>                  </valueentry>                </valuelist>                <value>1</value>              </parameter>              <parameter>                <parameterid>align</parameterid>                <name>Alignment</name>                <valuemin>1</valuemin>                <valuemax>3</valuemax>                <valuelist>                  <valueentry>                    <name>Left</name>                    <value>1</value>                  </valueentry>                  <valueentry>                    <name>Center</name>                    <value>2</value>                  </valueentry>                  <valueentry>                    <name>Right</name>                    <value>3</value>                  </valueentry>                </valuelist>                <value>2</value>              </parameter>              <parameter>                <parameterid>size</parameterid>                <name>Size</name>                <valuemin>0</valuemin>                <valuemax>200</valuemax>                <value>25</value>              </parameter>              <parameter>                <parameterid>track</parameterid>                <name>Tracking</name>                <valuemin>0</valuemin>                <valuemax>100</valuemax>                <value>1</value>              </parameter>              <parameter>                <parameterid>lead</parameterid>                <name>Leading</name>                <valuemin>-100</valuemin>                <valuemax>100</valuemax>                <value>0</value>              </parameter>              <parameter>                <parameterid>aspect</parameterid>                <name>Aspect</name>                <valuemin>0</valuemin>                <valuemax>4</valuemax>                <value>1</value>              </parameter>              <parameter>                <parameterid>linewidth</parameterid>                <name>Line Width</name>                <valuemin>0</valuemin>                <valuemax>200</valuemax>                <value>2</value>              </parameter>              <parameter>                <parameterid>linesoft</parameterid>                <name>Line Softness</name>                <valuemin>0</valuemin>                <valuemax>100</valuemax>                <value>5</value>              </parameter>              <parameter>                <parameterid>textopacity</parameterid>                <name>Text Opacity</name>                <valuemin>0</valuemin>                <valuemax>100</valuemax>                <value>100</value>              </parameter>              <parameter>                <parameterid>center</parameterid>                <name>Center</name>                <value>                  <horiz>0.058</horiz>                  <vert>0.421</vert>                </value>              </parameter>              <parameter>                <parameterid>textcolor</parameterid>                <name>Text Color</name>                <value>                  <alpha>255</alpha>                  <red>0</red>                  <green>0</green>                  <blue>0</blue>                </value>              </parameter>              <parameter>                <parameterid>supertext</parameterid>                <name>Text Graphic</name>              </parameter>              <parameter>                <parameterid>superline</parameterid>                <name>Line Graphic</name>              </parameter>              <parameter>                <parameterid>part2</parameterid>                <name>Background Settings</name>                <value/>              </parameter>              <parameter>                <parameterid>xscale</parameterid>                <name>Horizontal Size</name>                <valuemin>0</valuemin>                <valuemax>200</valuemax>                <value>0</value>              </parameter>              <parameter>                <parameterid>yscale</parameterid>                <name>Vertical Size</name>                <valuemin>0</valuemin>                <valuemax>200</valuemax>                <value>0</value>              </parameter>              <parameter>                <parameterid>xoffset</parameterid>                <name>Horizontal Offset</name>                <valuemin>-100</valuemin>                <valuemax>100</valuemax>                <value>0</value>              </parameter>              <parameter>                <parameterid>yoffset</parameterid>                <name>Vertical Offset</name>                <valuemin>-100</valuemin>                <valuemax>100</valuemax>                <value>0</value>              </parameter>              <parameter>                <parameterid>backsoft</parameterid>                <name>Back Soft</name>                <valuemin>0</valuemin>                <valuemax>100</valuemax>                <value>0</value>              </parameter>              <parameter>                <parameterid>backopacity</parameterid>                <name>Back Opacity</name>                <valuemin>0</valuemin>                <valuemax>100</valuemax>                <value>50</value>              </parameter>              <parameter>                <parameterid>backcolor</parameterid>                <name>Back Color</name>                <value>                  <alpha>255</alpha>                  <red>255</red>                  <green>255</green>                  <blue>255</blue>                </value>              </parameter>              <parameter>                <parameterid>superback</parameterid>                <name>Back Graphic</name>              </parameter>              <parameter>                <parameterid>crop</parameterid>                <name>Crop</name>                <value>false</value>              </parameter>              <parameter>                <parameterid>autokern</parameterid>                <name>Auto Kerning</name>                <value>true</value>              </parameter>            </effect>            <sourcetrack>              <mediatype>video</mediatype> <trackindex>1</trackindex>            </sourcetrack>          </generatoritem>"

                result_2 += str6_2 + start_time_2 + str8_2 + end_time_2 + str10_2 + start_time_2 + str12_2 + end_time_2 + str14_2 + text_2 + str16_2
                timeCnt += time_for_text

            lineCnt += 1

    ## 자막 배경 넣는 부분 ( 레이어2개가 들어가지 않아서 실패 ) ##
    # background_1 = "<clipitem><name>잡식왕_자막배경.png</name><duration>382.80000000000007</duration><rate><ntsc>TRUE</ntsc><timebase>30</timebase></rate><start>0</start><end>"
    # time
    # background_3 = "< / end > < in > 0 < / in > < out >"
    # time
    # background_5 = "</out><stillframe>TRUE</stillframe><file id=\"잡식왕_자막배경.png\"><name>잡식왕_자막배경.png</name><pathurl>잡식왕_자막배경.png</pathurl><duration>2</duration><media><video><duration>2</duration><stillframe>TRUE</stillframe><samplecharacteristics><width>720</width><height>480</height></samplecharacteristics></video></media></file><filter><effect id = \"basicmotion\"><name>Basic Motion</name><effectid>basic</effectid><effectcategory>motion</effectcategory><effecttype>motion</effecttype><mediatype>video</mediatype><parameter><parameterid>scale</parameterid><name>Scale</name> <valuemin>0</valuemin><valuemax>1000</valuemax><value>25</value></parameter><parameter><parameterid>center</parameterid><name>Center</name><value><horiz>-2.98023e-08</horiz><vert>-0.00524935</vert></value></parameter></effect></filter><sourcetrack><mediatype>video</mediatype><trackindex>1</trackindex></sourcetrack></clipitem>"
    # result += background_1 + str(time) + background_3 + str(time) + background_5

    ## 반복 ##
    str17 = "< / track > < / video > < / media > < / sequence > < / xmeml > "

    result += str17
    result_2 += str17

    writexml = open('./static/output/자막_'+question_id+'_line1.xml', 'w', encoding="utf-8")
    writexml.write(result)
    writexml.close()

    writexml = open('./static/output/자막_'+question_id+'_line2.xml', 'w', encoding="utf-8")
    writexml.write(result_2)
    writexml.close()


    """
    파일 다운로드 받기 
    참고 : https://parkhyeonchae.github.io/2020/04/12/django-project-24/
    """

    with zipfile.ZipFile('./static/output/자막_' + question_id + '_' + now.strftime('%Y%m%d') + '.zip', 'w', compression=zipfile.ZIP_DEFLATED) as new_zip:
        new_zip.write('./static/output/자막_' + question_id + '_line1.xml', arcname='line1.xml')
        new_zip.write('./static/output/자막_' + question_id + '_line2.xml', arcname='line2.xml')

    with open('./static/output/자막_' + question_id + '_' + now.strftime('%Y%m%d') + '.zip', 'rb') as fh:
        quote_file_url = urllib.parse.quote('자막_'+ question_id + '_' + now.strftime('%Y%m%d')+'.zip')
        response = HttpResponse(fh.read(), content_type='zip')
        response['Content-Disposition'] = 'attachment;filename*=UTF-8\'\'%s' % quote_file_url
        return response

    raise Http404



@login_required(login_url='common:login')
def editor_keyword(request):
    """
    키워드로 검색 후 다운로드 받아 압축하기
    """

    keywords = request.POST.get('keywords', '')
    question_id = request.POST.get('qid', '')

    print(keywords)
    print(question_id)

    downloadPath = './static/keyword/' + question_id + '/'
    if not os.path.isdir(downloadPath):
        os.mkdir(downloadPath)


    ## 기존 다운로드 폴더에 있던 파일들 모두 지우기 ##
    org_file_list = os.listdir(downloadPath)
    for list in org_file_list:
        #print(list)
        os.remove(downloadPath + list)

    with open('./static/output/keyword_' + question_id + '.txt', "w", encoding="utf8") as f:
        f.write(keywords)

    keywords = keywords.split('\n')


    for keyword in keywords:
        print('keyword : ' + keyword)
        key = keyword.split('|')
        cnt = 1
        num = ''
        for k in key:
            if cnt == 3:
                break
            if cnt == 1:
                num = k
            if cnt == 2:
                if k.find('[') > -1 and k.find(']') > -1:
                    downloadFile(num, k, question_id)
                    continue

                k = k.split(',')
                for down_key in k:
                    down_key = down_key.strip()
                    downloadFile(num, down_key, question_id)
            cnt += 1



    file_list = os.listdir(downloadPath)
    for list in file_list:
        print(list)


    #with zipfile.ZipFile(downloadPath + 'keyword.zip', 'w', compression=zipfile.ZIP_DEFLATED) as new_zip:
    with zipfile.ZipFile('./static/output/' + 'keyword_' + question_id + '.zip', 'w') as new_zip:
        for list in file_list:
            print(list)
            new_zip.write(downloadPath + list, arcname=list)

    with open('./static/output/' + 'keyword_' + question_id + '.zip', 'rb') as fh:
        quote_file_url = urllib.parse.quote('keyword.zip')
        response = HttpResponse(fh.read(), content_type='zip')
        response['Content-Disposition'] = 'attachment;filename*=UTF-8\'\'%s' % quote_file_url
        editor_modify_download_true(question_id)
        return response

    raise Http404

    return HttpResponse(json.dumps("success"), content_type="application/json")



@login_required(login_url='common:login')
def editor_keyword_select_download(request):
    """
    키워드로 검색 후 다운로드 받아 압축하기
    """

    keywords = request.POST.get('keywords', '')
    question_id = request.POST.get('qid', '')

    print(keywords)
    print(question_id)
    downloadPath = './static/keyword/' + question_id + '/'
    if not os.path.isdir(downloadPath):
        os.mkdir(downloadPath)

    ## 기존 다운로드 폴더에 있던 파일들 모두 지우기 ##
    org_file_list = os.listdir(downloadPath)
    for list in org_file_list:
        # print(list)
        os.remove(downloadPath + list)

    keywords = keywords.split('\n')

    for keyword in keywords:
        #print('keyword : ' + keyword)
        key = keyword.split('|')
        #print(key)
        line_num = key[0].split('_')[2]
        img_num = key[0].split('_')[3]
        download_url = key[1]


        if download_url.find('heemkim') > 0:
            resourcePath = 'C:\YouTube\99. 자료'
            download_url_path = urllib.parse.unquote(download_url)
            download_url_path = download_url_path.replace('http://heemkim.ddns.net:8000/static/resources',resourcePath)
            download_url_path = download_url_path.replace('.png', '.mp4')
            print('local file copy : ' + download_url_path)

            ## 로컬드라이브에서 -> 정해진위치에 파일 복사 ##
            ## mp4를 기본으로 바라보고 없으면 mov ##

            if os.path.isfile(download_url_path):
                shutil.copy(download_url_path, downloadPath)
            else:
                try:
                    download_url_path = download_url_path.replace('.mp4', '.mov')
                    shutil.copy(download_url_path, downloadPath)
                except:
                    continue
            filename_1 = str(download_url_path).split("/")[-1].split(".")[0]
            filename_2 = str(download_url_path).split("/")[-1].split(".")[1]
            print("download_url_path : " + download_url_path)
            print("filename_1 : " + filename_1)
            print("filename_2 : " + filename_2)

            # shutil.move(filename_1+"."+filename_2, str(cnt) + '.' + keyword + '_' + str(downloadCnt) + filename_2)
            ## 파일명 변경 ##
            os.rename(downloadPath + filename_1 + "." + filename_2,
                    downloadPath + str(line_num) + '_' + str(img_num) + ".mp4")


        else:
            print('google file download : ' + download_url)

            url = download_url
            req = Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                'Accept-Encoding': 'none',
                'Accept-Language': 'en-US,en;q=0.8',
                'Connection': 'keep-alive'})

            # print("[Request URL] : " + url)

            try:
                html = urlopen(req)
            except HTTPError as e:
                print('HTTPError')
                continue
            except URLError as e:
                print('URLError')
                continue

            googleimgUrlArr = []
            with html as f:
                with open(downloadPath + str(line_num) + '_' + str(img_num) + '.' + url[-4:],
                          'wb') as h:  # w - write b - binary
                    img = f.read()
                    h.write(img)


    file_list = os.listdir(downloadPath)
    for list in file_list:
        print(list)

    # with zipfile.ZipFile(downloadPath + 'keyword.zip', 'w', compression=zipfile.ZIP_DEFLATED) as new_zip:
    with zipfile.ZipFile('./static/output/' + 'keyword_' + question_id + '.zip', 'w') as new_zip:
        for list in file_list:
            print(list)
            new_zip.write(downloadPath + list, arcname=list)

    editor_modify_download_true(question_id)
    # with open('./static/output/' + 'keyword_' + question_id + '.zip', 'rb') as fh:
    #     quote_file_url = urllib.parse.quote('keyword.zip')
    #     response = HttpResponse(fh.read(), content_type='zip')
    #     response['Content-Disposition'] = 'attachment;filename*=UTF-8\'\'%s' % quote_file_url
    #     return response

    #raise Http404

    question = get_object_or_404(Question, pk=question_id)
    #r = send_to_kakao(question.subject)

    #r = get_kakao_friend()
    #print(r.text)

    #r = send_to_kakao_for_friend(question.subject)
    #print(r.text)

    return HttpResponse(json.dumps("success"), content_type="application/json")





@login_required(login_url='common:login')
def editor_keyword_search(request):
    """
    키워드로 검색 리스트 뽑기
    """

    keywords = request.POST.get('keywords', '')
    question_id = request.POST.get('qid', '')

    print(keywords)
    print(question_id)

    keywords = keywords.split('\n')

    for keyword in keywords:
        key = keyword.split('|')
        cnt = 1
        num = ''
        for k in key:
            if cnt == 3:
                break
            if cnt == 1:
                num = k
            if cnt == 2:
                if k.find('[') > -1 and k.find(']') > -1:
                    searchFile(num, k, question_id)
                    continue

                k = k.split(',')
                for down_key in k:
                    down_key = down_key.strip()
                    context = searchFile(num, down_key, question_id)
            cnt += 1


    return HttpResponse(json.dumps(context), content_type="application/json; charset=utf=8")




@login_required(login_url='common:login')
def editor_keyword_save(request):
    """
    키워드 저장하기
    """

    keywords = request.POST.get('keywords', '')
    question_id = request.POST.get('qid', '')
    print(keywords)
    print(question_id)

    with open('./static/output/keyword_' + question_id + '.txt', "w", encoding="utf8") as f:
        f.write(keywords)

    return HttpResponse(json.dumps("success"), content_type="application/json")



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

def downloadFile(cnt, keyword, question_id):
    """
    키워드에 맞는 파일 다운로드 하기
    """
    resourceFilePath = 'C:\YouTube\99. 자료'
    resourceCnt = 4
    downloadPath = './static/keyword/' + question_id + '/'


    # 다운로드 받을 개수 cnt
    downloadCnt = 1
    downloadMax = int(resourceCnt)
    print("[Search Keyworkd] : " + keyword)

    # http로 시작할 경우 웹페이지의 title을 따온다 #
    if keyword[0:4] == 'http':
        ## 0. http로 시작할경우 h1 태그 가져오기 ##
        url = keyword

        req = Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'})

        try:
            html = urlopen(req)
        except HTTPError as e:
            print('h1 tag HTTPError')
        except URLError as e:
            print('h1 tag URLError')


        soup = bs(html, "html.parser")

        search_header = ''
        #og_title = soup.find("meta", property="og:title")['content']
        og_title = soup.find("meta", property="og:title")
        title = soup.find("title")

        #print("title : " + str(title))
        #print("og_title : " + str(og_title))


        if og_title is not None:
            og_title = str(og_title['content'])
            search_header = str(og_title)
        elif title is not None:
            title = title.text
            search_header = str(title)
        else:
            return

        search_header = search_header.replace(' | 연합뉴스','')
        search_header = search_header.replace(' - 세계일보', '')

        print('h1 키워드 : ' + keyword + ' ' + search_header)
        fontname = "./static/font/NanumBarunGothicBold.ttf"
        fontsize = 70
        text = search_header

        colorText = "black"
        colorOutline = "red"
        colorBackground = "white"

        font = ImageFont.truetype(fontname, fontsize)
        width, height = getSize(text, font)
        img = Image.new('RGB', (width + 20, height + 60), colorBackground)
        d = ImageDraw.Draw(img)
        d.text((2, height / 2), text, fill=colorText, font=font)
        d.rectangle((0, 0, width + 10, height + 60))  # , outline=colorOutline)
        img.save(downloadPath + str(cnt) + '.' + '제목_' + str(datetime.datetime.now().timestamp()) + '.png')

        return

    # [ ] 안에 있을 경우 제목이미지 생성 #
    if keyword.find('[') > -1 and keyword.find(']') > -1:
        keyword = keyword.replace('[','')
        keyword = keyword.replace(']', '')
        fontname = "./static/font/NanumBarunGothicBold.ttf"
        fontsize = 70
        text = keyword

        colorText = "black"
        colorOutline = "red"
        colorBackground = "white"

        font = ImageFont.truetype(fontname, fontsize)
        width, height = getSize(text, font)
        img = Image.new('RGB', (width + 20, height + 60), colorBackground)
        d = ImageDraw.Draw(img)
        d.text((2, height / 2), text, fill=colorText, font=font)
        d.rectangle((0, 0, width + 10, height + 60))  # , outline=colorOutline)
        img.save(downloadPath + str(cnt) + '.' + '제목_' + str(datetime.datetime.now().timestamp()) + '.png')

        return

    ## 1. local pc에서 파일 검색 ##
    ## 다운로드 받을 파일 경로 ##
    # resourcePath = "C:/YouTube/04. 무료동영상"
    # downloadPath = './images'
    print('local file 검색 시작')
    resourcePath = resourceFilePath

    localFileArr = []
    for (path, dir, files) in os.walk(resourcePath):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            # if ext == '.mp4':
            #    print("%s/%s" % (path, filename))
            # if ext == '.mov':
            #    print("%s/%s" % (path, filename))

            name = os.path.splitext(filename)[0]
            name_str = str(name)
            if name_str.find(keyword) > -1:
                localFileArr.append("%s/%s" % (path, filename))
                print("%s/%s" % (path, filename))

    localFileCnt = localFileArr.__len__()
    print('localFileCnt : ')
    print(localFileCnt)
    print('downloadCnt : ')
    print(downloadCnt)
    print('downloadMax : ')
    print(downloadMax)

    if not localFileArr:
        print("local file is null")
    else:
        while downloadCnt <= downloadMax:
            if downloadCnt == localFileCnt + 1:
                break
            print(localFileArr)
            ## 검색 결과에서 1개 랜덤 뽑기 ##
            selectFile = random_pop(localFileArr)
            ## 로컬드라이브에서 -> 정해진위치에 파일 복사 ##
            shutil.copy(selectFile, downloadPath)
            filename_1 = str(selectFile).split("/")[-1].split(".")[0]
            filename_2 = str(selectFile).split("/")[-1].split(".")[1]
            print("selectFile : " + selectFile)
            print("filename_1 : " + filename_1)
            print("filename_2 : " + filename_2)

            # shutil.move(filename_1+"."+filename_2, str(cnt) + '.' + keyword + '_' + str(downloadCnt) + filename_2)
            ## 파일명 변경 ##
            os.rename(downloadPath + filename_1 + "." + filename_2,
                      downloadPath + str(cnt) + '.' + keyword + '_' + str(downloadCnt) + "." + filename_2)
            downloadCnt += 1

    ## 5개가 되었는지 체크 ##
    print(downloadCnt)
    print(downloadMax)
    if downloadCnt > downloadMax:
        return

    ## 2. pixabay에서 비디오 검색 ##
    print('pixabay 검색 시작')
    baseUrl = 'https://pixabay.com/ko/videos/search/'
    url = baseUrl + quote_plus(keyword)  # 한글 검색 자동 변환
#   url = 'https://pixabay.com/ko/videos/search/%EC%BD%94%EB%A1%9C%EB%82%98/?pagi=2' # url 강제 지정해서 다운로드
    req = Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'})

    try:
        html = urlopen(req)
    except HTTPError as e:
        print('pixabay HTTPError')
    except URLError as e:
        print('pixabay URLError')


    soup = bs(html, "html.parser")
    video = soup.select('div.flex_grid.video.search_results > div > a')
    print('pixabay 키워드 : ' + keyword + ' ' + str(video))
    imgUrlArr = []

    # 한방에 번호 찾기
    # content > div.media_list > div:nth-child(3) > div > div.flex_grid.video.search_results > div:nth-child(23) > a
    video_detail = soup.select('div.flex_grid.video.search_results > div > a')

    for j in video_detail:
        videoId = j['href']
        print(videoId)
        videoSplit = videoId.split('-');
        videoNum = videoSplit[-1]
        videoNum = videoNum.replace('/', '')
        print(videoNum)
        videoUrl = "https://pixabay.com/ko/videos/download/video-" + videoNum + "_large.mp4"
        print('pixabay 상세 페이지 : ' + videoUrl)
        imgUrlArr.append((videoUrl))



    # for i in video:
    #     # if imgUrlArr.__len__() == 3: #개수제한을 강제로 걸어버리기
    #     #     break
    #     videoUrl = i['href']
    #     videoUrl = "https://pixabay.com" + videoUrl
    #
    #     req = Request(videoUrl, headers={
    #         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    #         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    #         'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    #         'Accept-Encoding': 'none',
    #         'Accept-Language': 'en-US,en;q=0.8',
    #         'Connection': 'keep-alive'})
    #
    #     try:
    #         html = urlopen(req)
    #     except HTTPError as e:
    #         print('pixabay HTTPError')
    #     except URLError as e:
    #         print('pixabay URLError')

        # soup = bs(html, "html.parser")
        # video_detail = soup.select('div.flex_grid.video.affil_videos')
        # # content > div > div:nth-child(3) > div > div.flex_grid.video.search_results > div:nth-child(1) > a
        # #print(video)
        # #media_show > div:nth-child(5) > div:nth-child(1) > div.flex_grid.video.affil_videos.affil_medias
        # for j in video_detail:
        #     videoId = j['data-media-id']
        #     videoUrl = "https://pixabay.com/ko/videos/download/video-" + videoId + "_large.mp4"
        #     print('pixabay 상세 페이지 : ' + videoUrl)
        #     imgUrlArr.append((videoUrl))


    imgCnt = imgUrlArr.__len__()

    if not video:
        print("img is null")
    else:
        # videoUrl의 파일을 다운로드 받는다
        while downloadCnt <= downloadMax:
            print(str(downloadCnt) + " : " + str(downloadMax))
            select = random_pop(imgUrlArr)
            if select is None:
                break
            print("ramdon_pop pixabay : " + select)
            try:
                req = Request(select, headers={
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    'Accept-Encoding': 'none',
                    'Accept-Language': 'en-US,en;q=0.8',
                    'Connection': 'keep-alive'})
                html = urlopen(req)
            except HTTPError as e:
                print("HTTPError")
                continue
            except URLError as e:
                print("URLError")
                continue
            with html as f:
                with open(downloadPath + str(cnt) + '.' + keyword + '_' + str(downloadCnt) + '.mp4',
                          'wb') as h:  # w - write b - binary
                    video = f.read()
                    h.write(video)
            downloadCnt += 1

    ## 5개가 되었는지 체크 ##
    if downloadCnt >= downloadMax:
        return



    # 3. google에서 이미지 검색 ##
    print('google 검색 시작')
    if downloadCnt < downloadMax:
        print("img keyword google")
        url = "https://www.google.com/search?q=" + str(quote_plus(keyword)) + "&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiB_JTClpzrAhWOd94KHQy4BEsQ_AUoAnoECBoQBA&cshid=1597459025236061&biw=2560&bih=1297"
        req = Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'})

        print("[Request URL] : " + url)

        try:
            html = urlopen(req)
        except HTTPError as e:
            print('google HTTPError')
        except URLError as e:
            print('google URLError')

        soup = bs(html, "html.parser")

        with open(downloadPath + 'search.html', "w", encoding="utf8") as f:
            f.write(soup.prettify())

        googleimgUrlArr = []
        with open(downloadPath + 'search.html', "r", encoding="utf8") as f:
            search_cnt = 0
            html_str = f.read()
            keyword2 = html_str.split('"');
            for key in keyword2:
                protocol = key[0:4]
                ext = key[-4:]
                if search_cnt > 20:
                    break
                if ext == ".png" or ext == ".jpg":
                    if protocol == "http" and key.find("www.google.com") < 0 and key.find("www.youtube.com") < 0 and key.find("www.ytn.co.kr") < 0:
                        print(str(search_cnt) + " : " + key + " : " + key[-4:])
                        googleimgUrlArr.append(key)
                        search_cnt += 1



        while downloadCnt <= downloadMax:
            print("downloadCnt : " + str(downloadCnt) + ", downloadMax : " + str(downloadMax))
            select = random_pop(googleimgUrlArr)
            if select is None:
                break
            print("ramdon_pop google : " + select)
            try:
                html = urlopen(select)
            except HTTPError as e:
                print("HTTPError")
                continue
            except URLError as e:
                print("URLError")
                continue
            with html as f:
                with open(downloadPath + str(cnt) + '.' + keyword + '_' + str(downloadCnt) + select[-4:],
                          'wb') as h:  # w - write b - binary
                    img = f.read()
                    h.write(img)
                    print(str(downloadCnt) + " : " + str(select))
            downloadCnt += 1

    print('Image Crawling & download is done.')


def searchFile(cnt, keyword, question_id):
    """
    키워드에 맞는 파일 검색해서 리스트 뽑기
    """
    #resourceFilePath = 'D:\YouTube\99. 자료'
    resourceFilePath = './static/resources'
    resourceCnt = 4
    downloadPath = './static/keyword/' + question_id + '/'
    outputList = []

    # 다운로드 받을 개수 cnt
    downloadCnt = 1
    downloadMax = int(resourceCnt)
    print("[Search Keyworkd] : " + keyword)

    # http로 시작할 경우 웹페이지의 title을 따온다 #
    if keyword[0:4] == 'http':
        return

    # [ ] 안에 있을 경우 제목이미지 생성 #
    if keyword.find('[') > -1 and keyword.find(']') > -1:
        # keyword = keyword.replace('[', '')
        # keyword = keyword.replace(']', '')
        # fontname = "./static/font/NanumBarunGothicBold.ttf"
        # fontsize = 70
        # text = keyword
        #
        # colorText = "black"
        # colorOutline = "red"
        # colorBackground = "white"
        #
        # font = ImageFont.truetype(fontname, fontsize)
        # width, height = getSize(text, font)
        # img = Image.new('RGB', (width + 20, height + 60), colorBackground)
        # d = ImageDraw.Draw(img)
        # d.text((2, height / 2), text, fill=colorText, font=font)
        # d.rectangle((0, 0, width + 10, height + 60))  # , outline=colorOutline)
        # img.save(downloadPath + str(cnt) + '.' + '제목_' + str(datetime.datetime.now().timestamp()) + '.png')
        return

    ## 1. local pc에서 파일 검색 ##
    ## 다운로드 받을 파일 경로 ##
    # resourcePath = "C:/YouTube/04. 무료동영상"
    # downloadPath = './images'
    resourcePath = resourceFilePath

    localFileArr = []
    for (path, dir, files) in os.walk(resourcePath):
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            name = os.path.splitext(filename)[0]
            name_str = str(name)
            if name_str.find(keyword) > -1:
                #localFileArr.append("%s\%s" % (path, filename))
                if ext == '.png':
                    #localFileArr.append("/static/resources/%s" % (filename))
                    path = path.replace('./','/')
                    localFileArr.append(path+'/'+filename)
                #print("%s/%s" % (path, filename))

    localFileCnt = localFileArr.__len__()

    if not localFileArr:
        print("local file is null")
    else:
        while downloadCnt <= downloadMax:
            if downloadCnt == localFileCnt + 1:
                break
            #print(localFileArr)
            ## 검색 결과에서 1개 랜덤 뽑기 ##
            selectFile = random_pop(localFileArr)
            print('select local file : ' + selectFile)
            #selectFile = str(quote_plus(selectFile))
            selectFile = str(urllib.parse.quote(selectFile))
            selectFile = selectFile.replace('%2F','/')
            selectFile = selectFile.replace('+', '%20')
            outputList.append(selectFile)
            downloadCnt += 1



    ## 5개가 되었는지 체크 ##
    if downloadCnt > downloadMax:
        M = dict(zip(range(1, len(outputList) + 1), outputList))
        M['num'] = cnt
        return M

#     ## 2. pixabay에서 비디오 검색 ##
#     baseUrl = 'https://pixabay.com/ko/videos/search/'
#     url = baseUrl + quote_plus(keyword)  # 한글 검색 자동 변환
# #   url = 'https://pixabay.com/ko/videos/search/%EC%BD%94%EB%A1%9C%EB%82%98/?pagi=2' # url 강제 지정해서 다운로드
#     req = Request(url, headers={
#         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#         'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
#         'Accept-Encoding': 'none',
#         'Accept-Language': 'en-US,en;q=0.8',
#         'Connection': 'keep-alive'})
#
#     try:
#         html = urlopen(req)
#     except HTTPError as e:
#         print('pixabay HTTPError')
#     except URLError as e:
#         print('pixabay URLError')
#
#
#     soup = bs(html, "html.parser")
#     video = soup.select('div.flex_grid.video.search_results > div > a')
#     #print('pixabay 키워드 : ' + keyword + ' ' + str(video))
#     imgUrlArr = []
#
#     # 한방에 번호 찾기
#     # content > div.media_list > div:nth-child(3) > div > div.flex_grid.video.search_results > div:nth-child(23) > a
#     video_detail = soup.select('div.flex_grid.video.search_results > div > a')
#
#     for j in video_detail:
#         videoId = j['href']
#         #print(videoId)
#         videoSplit = videoId.split('-');
#         videoNum = videoSplit[-1]
#         videoNum = videoNum.replace('/', '')
#         #print(videoNum)
#         videoUrl = "https://pixabay.com/ko/videos/download/video-" + videoNum + "_large.mp4"
#         #print('영상url : ' + videoUrl)
#         imgUrlArr.append((videoUrl))
#
#
#     imgCnt = imgUrlArr.__len__()
#
#     if not video:
#         print("pixabay is null")
#     else:
#         # videoUrl의 파일을 다운로드 받는다
#         while downloadCnt <= downloadMax:
#             #print(str(downloadCnt) + " : " + str(downloadMax))
#             select = random_pop(imgUrlArr)
#             if select is None:
#                 break
#             print("select pixabay url : " + select)
#
#             downloadCnt += 1
#
#     ## 5개가 되었는지 체크 ##
#     if downloadCnt >= downloadMax:
#         return



    # 3. google에서 이미지 검색 ##
    #print('google 검색 시작')
    if downloadCnt < downloadMax:

        url = "https://www.google.com/search?q=" + str(quote_plus(keyword)) + "&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiB_JTClpzrAhWOd94KHQy4BEsQ_AUoAnoECBoQBA&cshid=1597459025236061&biw=2560&bih=1297"
        req = Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'})

        #print("[Request URL] : " + url)

        try:
            html = urlopen(req)
        except HTTPError as e:
            print('google HTTPError')
        except URLError as e:
            print('google URLError')

        googleimgUrlArr = []

        search_cnt = 0
        html_str = str(html.read())

        keyword2 = html_str.split('"');
        for key in keyword2:
            protocol = key[0:4]
            ext = key[-4:]
            if search_cnt > 20:
                break
            if ext == ".png" or ext == ".jpg":
                if protocol == "http" and key.find("www.google.com") < 0 and key.find("www.youtube.com") < 0 and key.find("www.ytn.co.kr") < 0:
                    #print(str(search_cnt) + " : " + key + " : " + key[-4:])
                    googleimgUrlArr.append(key)
                    search_cnt += 1


        while downloadCnt <= downloadMax:
            #print("downloadCnt : " + str(downloadCnt) + ", downloadMax : " + str(downloadMax))
            select = random_pop(googleimgUrlArr)
            if select is None:
                break
            print("select google image : " + select)
            outputList.append(select)
            downloadCnt += 1


    M = dict(zip(range(1, len(outputList) + 1), outputList))
    M['num'] = cnt
    return M

    print('Image Crawling is done.')




KAKAO_TOKEN = "9cFyITmgIVxuqTCU4ltvJQqTU4XXEs_uTbAVbgopyV4AAAF1iZM_OQ"
def send_to_kakao(text):
    header = {"Authorization": 'Bearer ' + KAKAO_TOKEN}
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    post = {
        "object_type": "text",
        "text": text,
        "link": {
            "web_url": "https://developers.kakao.com",
            "mobile_web_url": "https://developers.kakao.com"
        },
    }

    data = {"template_object": json.dumps(post)}
    return requests.post(url, headers=header, data=data)


def send_to_kakao_for_friend(text):
    header = {
        "Authorization": 'Bearer ' + KAKAO_TOKEN
    }
    url = "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"
    post = {
        "object_type": "feed",
        "content": {
            "title": "디저트 사진",
            "description": "아메리카노, 빵, 케익",
            "image_url": "http://mud-kage.kakao.co.kr/dn/NTmhS/btqfEUdFAUf/FjKzkZsnoeE4o19klTOVI1/openlink_640x640s.jpg",
            "image_width": 640,
            "image_height": 640,
            "link": {
            "web_url": "http://www.daum.net",
            "mobile_web_url": "http://m.daum.net",
            "android_execution_params": "contentId=100",
            "ios_execution_params": "contentId=100"
            }
        },
    }

    data = {"template_object": json.dumps(post), "receiver_uuids":  "[\"y_PK8sr-zPzQ49Lk0Ojc6Nn1wfjB9sf_jQ\"]"}
    return requests.post(url, headers=header, data=data)


def get_kakao_friend():
    header = {
        "Authorization": 'Bearer ' + KAKAO_TOKEN
    }

    url = "https://kapi.kakao.com/v1/api/talk/friends?friend_order=favorite&limit=100&order=asc"

    return requests.get(url, headers=header)
