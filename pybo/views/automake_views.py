from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Q
import json
import datetime

import urllib
import os
import zipfile
import shutil
import random
from urllib import parse
from urllib.request import Request
from PIL import Image, ImageDraw, ImageFont
from datetime import timedelta

from ..forms import YoutubeForm
from ..models import Youtube
from ..views import slack


@login_required(login_url='common:login')
def automake(request):
    """
    pybo 목록 출력
    """
    # 입력 파라미터
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어
    so = request.GET.get('so', 'recent')  # 정렬기준
    today = timezone.now() + timedelta(days=0)
    tomorrow = timezone.now() + timedelta(days=1)

    # 정렬
    if so == 'create':
        question_list = Youtube.objects.order_by('-create_date')
    else:  # recent
        question_list = Youtube.objects.order_by('-upload_target', '-modify_date')

    # 검색
    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) |  # 제목검색
            Q(content__icontains=kw) |  # 내용검색
            Q(author__username__icontains=kw) # 질문 글쓴이검색
        ).distinct()

    # 페이징처리
    paginator = Paginator(question_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context = {'question_list': page_obj, 'page': page, 'kw': kw, 'so': so, 'today':today, 'tomorrow':tomorrow}  # <------ so 추가
    return render(request, 'pybo/automake_list.html', context)


@login_required(login_url='common:login')
def automake_create(request):
    """
    스크립트 등록
    """

    upload = request.POST.get('upload_target','')
    if upload == '':
        upload = timezone.now() + timedelta(days=7)
    else:
        upload = datetime.strptime(str(request.POST.get('upload_target', '')), "%y/%m/%d")
        upload = upload.replace(hour=9)


    if request.method == 'POST':
        form = YoutubeForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user  # 추가한 속성 author 적용
            question.create_date = timezone.now()
            question.upload_target = upload
            question.save()
            slack.send_slack('[automake_create] ' + question.subject + ' ' + str(question.create_date))
            return redirect('pybo:automake')
    else:
        form = YoutubeForm()
    context = {'form': form}
    return render(request, 'pybo/automake_form.html', context)


@login_required(login_url='common:login')
def automake_editor(request):
    """
    스크립트 등록
    """
    # if request.method == 'POST':
    #     form = YoutubeForm(request.POST)
    #     if form.is_valid():
    #         question = form.save(commit=False)
    #         question.author = request.user  # 추가한 속성 author 적용
    #         question.create_date = timezone.now()
    #         question.save()
    #         return redirect('pybo:index')
    # else:
    #     form = YoutubeForm()

    qid = request.POST.get('qid', '')
    print('[automake] qid : ' + qid)
    keywords = ''
    status = ''
    category = request.POST.get('category', '폰')
    thumbnail_text = ''
    thumbnail_url = ''
    thumbnail_bg = ''

    if qid == '':
        status = "내용"
    else:
        question = get_object_or_404(Youtube, pk=qid)
        status = question.status
        category = question.category
        thumbnail_text = question.thumbnail_text
        thumbnail_url = question.thumbnail_url
        thumbnail_bg = question.thumbnail_bg
        video_id = question.video_id


    outputPath = './static/output_2/'
    isFile = os.path.isfile(outputPath + 'keyword_'+ qid +'.txt')

    if isFile is True:
        with open(outputPath + 'keyword_'+ qid +'.txt', "r", encoding="utf8") as f:
            for line in f.readlines():
                keywords += line

    print('[automake] keywords : \n' + keywords)

    context = {'qid': request.POST.get('qid', ''),
               'subject': request.POST.get('subject', ''),
               'content': request.POST.get('content', ''),
               'keyword': keywords,
               'status': status,
               'category': category,
               'thumbnail_text': thumbnail_text,
               'thumbnail_url': thumbnail_url,
               'thumbnail_bg': thumbnail_bg,
               'video_id': video_id
               }
    #print(context)
    return render(request, 'pybo/automake_editor.html', context)



def automake_detail(request, question_id):
    """
    pybo 내용 출력
    """
    question = get_object_or_404(Youtube, pk=question_id)
    context = {'question': question}
    return render(request, 'pybo/automake_detail.html', context)



@login_required(login_url='common:login')
def automake_save(request):
    """
    pybo 질문등록
    """
    question_id = request.POST.get('qid', '')
    print(question_id)
    thumbnail_text = request.POST.get('thumbnail_text', '')
    print(thumbnail_text)
    thumbnail_bg = request.POST.get('thumbnail_bg', '')
    print(thumbnail_bg)
    thumbnail_url = '/static/output_2/thumb_'+question_id+'.png'

    if question_id == '':
        # create
        form = YoutubeForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user  # 추가한 속성 author 적용
            question.create_date = timezone.now()
            question.save()
            context = {'status': 'create', 'qid': question.id }
            return HttpResponse(json.dumps(context), content_type="application/json")
    else:
        # modify
        question = get_object_or_404(Youtube, pk=question_id)
        form = YoutubeForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            question.modify_date = timezone.now()  # 수정일시 저장
            question.thumbnail_text = thumbnail_text
            question.thumbnail_url = thumbnail_url
            question.thumbnail_bg = thumbnail_bg
            question.save()
            context = {'status': 'modify', 'qid': question.id}
            return HttpResponse(json.dumps(context), content_type="application/json")

@login_required(login_url='common:login')
def automake_modify(request, question_id):
    """
    스크립트 수정
    """
    question = get_object_or_404(Youtube, pk=question_id)

    # if request.user != question.author:
    #     messages.error(request, '수정권한이 없습니다')
    #     return redirect('pybo:detail', question_id=question.id)

    if request.method == "POST":
        form = YoutubeForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.modify_date = timezone.now()  # 수정일시 저장
            question.upload_target = timezone.now()  # 수정일시 저장
            question.save()
            slack.send_slack('[automake_modify] ' + question.subject + ' ' + str(question.create_date))
            return redirect('pybo:automake_detail', question_id=question.id)
    else:
        form = YoutubeForm(instance=question)
    context = {'form': form, 'upload_target':question.upload_target}
    return render(request, 'pybo/automake_form.html', context)


@login_required(login_url='common:login')
def automake_delete(request, question_id):
    """
    pybo 질문삭제
    """
    question = get_object_or_404(Youtube, pk=question_id)
    if request.user != question.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('pybo:automake_detail', question_id=question.id)
    question.delete()
    return redirect('pybo:automake')


def automake_modify_download_true(question_id):
    """
    pybo 다운로드 완료
    """
    question = get_object_or_404(Youtube, pk=question_id)
    print(question.status)
    print(question.create_date)
    question.download_flag = '1'
    question.save()
    return redirect('pybo:index')

def automake_modify_download_loading(question_id):
    """
    pybo 다운로드 완료
    """
    question = get_object_or_404(Youtube, pk=question_id)
    print(question.status)
    print(question.create_date)
    question.download_flag = '2'
    question.save()
    return redirect('pybo:index')

def automake_modify_download_false(question_id):
    """
    pybo 다운로드 완료
    """
    question = get_object_or_404(Youtube, pk=question_id)
    print('[automake_modify_download_false] status : ' + question.status)
    print('[automake_modify_download_false] create_date : ' + question.create_date)
    question.download_flag = '0'
    question.save()
    return redirect('pybo:index')

def automake_youtube_upload_true(question_id):
    """
    업로드 완료 플래그
    """
    question = get_object_or_404(Youtube, pk=question_id)
    print(question.status)
    print(question.create_date)
    question.upload_flag = '1'
    question.upload_target = timezone.now()
    question.save()

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def automake_youtube_upload_complete(request):
    """
    upload_youtube_sst.py 업로드 완료 후 호출
    """
    slack.send_slack('[automake_video] 유튜브 썸네일 업로드 시작')
    video_id = request.POST.get('video_id', '')
    print(video_id)

    filepath = request.POST.get('filepath', '')
    print(filepath)

    f_path = filepath
    f_path = f_path.replace('./static/output_2/thumb_','')
    f_path = f_path.replace('.png', '')
    question_id = f_path
    question = get_object_or_404(Youtube, pk=question_id)
    question.video_id = video_id
    question.save()


    import subprocess
    # run your program and collect the string output

    cmd = [
        'python',
        'upload_thumbnail.py',
        "--file=" + filepath,
        "--video-id=" + video_id
    ]
    out_str = subprocess.check_output(cmd, shell=True)
    print(out_str)

    slack.send_slack('[automake_video] 유튜브 썸네일 업로드 완료')
    context = {'status': 'success', 'video-id': video_id}
    return HttpResponse(json.dumps(context), content_type="application/json")


def automake_create_thumbnail(request):
    """
    썸네일 만들기
    """
    #slack.send_slack('[automake_create_thumbnail] 유튜브 썸네일 업로드 시작')
    question_id = request.POST.get('qid', '')
    print('question_id', question_id)

    thumbnail_text = request.POST.get('thumbnail_text', '')
    print('thumbnail_text', thumbnail_text)

    thumbnail_textsize = request.POST.get('thumbnail_textsize', '')
    print('thumbnail_textsize', thumbnail_textsize)

    thumbnail_bg = request.POST.get('thumbnail_bg', '')
    print('thumbnail_bg', thumbnail_bg)



    thumbnail_text_sp = thumbnail_text.split('\n')

    keyword_list = ['','','','']
    keyword_list[0] = ''
    keyword_list[1] = ''
    keyword_list[2] = ''
    keyword_list[3] = ''

    cnt=0
    for line in thumbnail_text_sp:
        print(line)
        keyword_list[cnt] = line
        cnt+=1

    ####### 썸네일 자동생성 #########
    keyword1 = keyword_list[0]
    keyword2 = keyword_list[1]
    keyword3 = keyword_list[2]
    keyword4 = keyword_list[3]

    width_start = 40
    height_start1 = 40
    height_start2 = 160
    height_start3 = 440
    height_start4 = 560
    font_size = int(thumbnail_textsize)
    font_type = 'Recipekorea 레코체 FONT.ttf'
    thumbnail_url = '/static/output_2/thumb_' + question_id + '.png'

    target_image = Image.open('./youtube/2/thumb_bg.png')  # 일단 기본배경폼 이미지를 open 합니다.
    fontsFolder = "./static/font/"  # 글자로 쓸 폰트 경로
    selectedFont = ImageFont.truetype(os.path.join(fontsFolder, font_type), font_size)  # 폰트경로과 사이즈를 설정해줍니다.
    draw = ImageDraw.Draw(target_image)


    thumb_bg = ''
    if thumbnail_bg != '':
        img_url = thumbnail_bg
        split1 = img_url.split('/')
        url_filename = split1[-1]
        print(url_filename)
        split2 = url_filename.split('.')
        filename, filename_2 = split2[-2], split2[-1]
        urllib.request.urlretrieve(img_url, './static/output_2/temp/thumbnail_bg_' + question_id + '.' + filename_2)
        thumb_bg = './static/output_2/temp/thumbnail_bg_' + question_id + '.' + filename_2
    else:
        thumb_bg = './youtube/2/thumb_bg.png'

    add_image = Image.open(thumb_bg)
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

    if width1 > width2:
        draw.rectangle((width_start1 + 20, height_start1 + 10, width_start1 + width1 - 10, height_start1 + 100),
                       fill="black")
        draw.rectangle((width_start2 + 20, height_start2 - 40, width_start2 + width2 - 10, height_start2 + 100),
                       fill="black")
    else:
        draw.rectangle((width_start1 + 20, height_start1 + 10, width_start1 + width1 - 10, height_start1 + 150),
                       fill="black")
        draw.rectangle((width_start2 + 20, height_start2 + 10, width_start2 + width2 - 10, height_start2 + 100),
                       fill="black")

    if width3 > width4:
        draw.rectangle((width_start3 + 20, height_start3 + 10, width_start3 + width3 - 10, height_start3 + 100),
                       fill="black")
        draw.rectangle((width_start4 + 20, height_start4 - 40, width_start4 + width4 - 10, height_start4 + 100),
                       fill="black")
    else:
        draw.rectangle((width_start3 + 20, height_start3 + 10, width_start3 + width3 - 10, height_start3 + 150),
                       fill="black")
        draw.rectangle((width_start4 + 20, height_start4 + 10, width_start4 + width4 - 10, height_start4 + 100),
                       fill="black")

    draw.text((width_start1 - 5, height_start1 - 5), keyword1, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start2 - 5, height_start2 - 5), keyword2, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start3 - 5, height_start3 - 5), keyword3, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start4 - 5, height_start4 - 5), keyword4, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정

    draw.text((width_start1 + 5, height_start1 - 5), keyword1, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start2 + 5, height_start2 - 5), keyword2, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start3 + 5, height_start3 - 5), keyword3, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start4 + 5, height_start4 - 5), keyword4, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정

    draw.text((width_start1 - 5, height_start1 + 5), keyword1, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start2 - 5, height_start2 + 5), keyword2, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start3 - 5, height_start3 + 5), keyword3, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start4 - 5, height_start4 + 5), keyword4, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정

    draw.text((width_start1 + 5, height_start1 + 5), keyword1, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start2 + 5, height_start2 + 5), keyword2, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start3 + 5, height_start3 + 5), keyword3, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start4 + 5, height_start4 + 5), keyword4, fill="black", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정

    draw.text((width_start1, height_start1), keyword1, fill="yellow", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start2, height_start2), keyword2, fill="yellow", font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start3, height_start3), keyword3, fill=(255, 255, 255), font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정
    draw.text((width_start4, height_start4), keyword4, fill=(255, 255, 255), font=selectedFont,
              align='center')  # fill= 속성은 무슨 색으로 채울지 설정,font=는 자신이 설정한 폰트 설정

    target_image.save('.'+thumbnail_url)  # 편집된 이미지를 저장합니다.


    #slack.send_slack('[automake_create_thumbnail] 유튜브 썸네일 업로드 완료')
    context = {'status': 'success', 'thumbnail_url': thumbnail_url}
    return HttpResponse(json.dumps(context), content_type="application/json")



@login_required(login_url='common:login')
def automake_convert(request):
    """
    스크립트 변환
    """
    content = request.POST.get('content', '없음')  # 페이지
    question_id = request.POST.get('qid', '')
    #print("content : ")
    #print(content)
    #print("qid : ")
    #print(question_id)

    output2 = ''
    fw = open('./static/output_2/script_'+question_id+'.txt', 'w', encoding="utf-8")

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

        ## xml 예약문자 처리 ##
        line = line.replace('&', ' and ')
        line = line.replace('<', '')
        line = line.replace('>', '')

        word = line.split(' ')
        for i in word:
            if i == "":
                continue

            charCnt += i.__len__()
            #print("charCnt : " + str(charCnt), i)

            if charCnt > 30:
                # lineStr += i
                # #print(lineCnt, lineStr, end="\n")
                # fw.write(lineStr + "\n")
                # output2 += i + "\n"
                # lineStr = ""
                # lineCnt = lineCnt + 1
                # charCnt = 0
                #print(lineCnt, lineStr, i, charCnt)
                fw.write("\n")
                output2 += "\n"
                lineStr += i + " "
                output2 += i + " "
                lineCnt = lineCnt + 1
                charCnt = i.__len__()
                #print(lineCnt, lineStr, i, charCnt)
            elif i.find("\n") > -1:
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


    fw.close()

    return HttpResponse(json.dumps(output2), content_type="application/json")


@login_required(login_url='common:login')
def automake_video(request):
    """
    부채널 자동화
    """

    slack.send_slack('[automake_video] start')

    # request 파라미터
    question_id = request.POST.get('qid', '')
    category = request.POST.get('category', '업무')

    question = get_object_or_404(Youtube, pk=question_id)
    automake_modify_download_loading(question_id)


    slack.send_slack('[automake_video] ' + question.subject)

    # 기본 변수 초기화
    result_subtitle_line1 = ''
    result_subtitle_line2 = ''
    result_subtitle_bg = ''
    result_image_logo = ''
    result_image = ''
    result_intro = ''
    result_outro = ''
    result_video = ''
    result_audio_voice = ''
    result_audio_bg = ''
    default_keyword = category
    intro_time = 600
    outro_time = 672



    # 폴더가 없을 경우 만들기
    downloadPath = './static/keyword_2/' + question_id + '/'
    outputPath = './static/output_2/script_' + question_id
    baseResourcePath = './youtube/2/'

    if not os.path.isdir(downloadPath):
        os.mkdir(downloadPath)

    # 기존 다운로드 폴더에 있던 파일들 모두 지우기
    org_file_list = os.listdir(downloadPath)
    for list in org_file_list:
        os.remove(downloadPath + list)
    ############################################################
    from ..models import Upload, Keyword
    # 키워드 뽑기
    dict = {}
    # 키워드 리스트
    keyword_list = Keyword.objects.order_by('-count')
    for keyword in keyword_list:
        # print(str(keyword.key) + ' : ' + str(keyword.value))
        if keyword.value is not None:
            dict[keyword.key] = keyword.value

    # 영상 태그 리스트
    tag_list = Upload.objects.order_by('-create_date')
    for list in tag_list:
        tags = list.tag.split(',')
        for tag in tags:
            dict[tag] = tag

    sdict = sorted(dict.items(), key=lambda item: len(item[0]), reverse=False)

    sorted_dict = {}
    for key, value in sdict:
        # print(str(key))
        # print(str(value))
        sorted_dict[key] = value

    # print(sorted_dict)
    slack.send_slack('[automake_video] 영상 태그, 커스텀 키워드 추출 완료')
    ############################################################

    # 스크립트 라인수 세기
    lineCnt = 0
    output = ''
    with open(outputPath + '.txt', 'r', encoding="utf-8") as file:
        for line in file.readlines():
            output += line
            line = line.replace('\n', '')
            lineCnt += 1


    # audio_voice API 호출해 다운로드 받아서 각 mp3 시간 구하기
    from mutagen.mp3 import MP3
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

    lineCnt_audio = 1
    lineSum = ''
    dict_audio_size = {}
    audio_size_sum = 0

    with open(outputPath + '.txt', 'r', encoding="utf-8") as file:
        for line in file.readlines():
            line = line.replace('\n', ' ')

            if lineCnt_audio % 2 == 0:
                lineSum += line
                encText = urllib.parse.quote(lineSum)
                print(encText)

                # Naver 음성 API 사용 (CSS)
                data = "speaker=nsinu&speed=-2&text=" + encText;
                response = urllib.request.urlopen(request_api, data=data.encode('utf-8'))
                rescode = response.getcode()
                if (rescode == 200):
                    print("TTS mp3 저장 : " + str(int(lineCnt_audio / 2)))
                    response_body = response.read()
                    with open(downloadPath + 'voice_' + str(int(lineCnt_audio / 2)) + '.mp3', 'wb') as f:
                        f.write(response_body)
                else:
                    print("Error Code:" + rescode)

                audiofile = downloadPath + 'voice_'+ str(int(lineCnt_audio / 2)) + '.mp3'
                audio = MP3(audiofile)
                print(str(int(lineCnt_audio / 2)), lineSum, int(audio.info.length * 60))
                dict_audio_size[str(int(lineCnt_audio / 2))] = int(audio.info.length * 60)
                audio_size_sum += int(audio.info.length * 60)
                lineSum = '' # 두줄단위로 끊어서 저장한 변수 초기화

            else:
                lineSum += line

                if lineCnt_audio == lineCnt:
                    encText = urllib.parse.quote(lineSum)
                    print(encText)

                    # Naver 음성 API 사용 (CSS)
                    data = "speaker=nsinu&speed=-2&text=" + encText;
                    response = urllib.request.urlopen(request_api, data=data.encode('utf-8'))
                    rescode = response.getcode()
                    if (rescode == 200):
                        print("TTS mp3 저장 : " + str(int(lineCnt_audio / 2 + 1)))
                        response_body = response.read()
                        with open(downloadPath + 'voice_' + str(int(lineCnt_audio / 2 + 1)) + '.mp3', 'wb') as f:
                            f.write(response_body)
                    else:
                        print("Error Code:" + rescode)

                    audiofile = downloadPath + 'voice_' + str(int(lineCnt_audio / 2 + 1)) + '.mp3'
                    audio = MP3(audiofile)
                    print(str(int(lineCnt_audio / 2 + 1)), lineSum, int(audio.info.length * 60))
                    dict_audio_size[str(int(lineCnt_audio / 2 + 1))] = int(audio.info.length * 60)
                    audio_size_sum += int(audio.info.length * 60)

            lineCnt_audio += 1

    slack.send_slack('[automake_video] 음성 다운로드 완료')


    ####################  자막 XML 생성  #####################

    lineCnt_subtitle = 0
    timeCnt  = 0
    with open(outputPath + '.txt', 'r', encoding="utf-8") as file:
        for line in file.readlines():
            line = line.replace('\n', ' ')

            if lineCnt_subtitle % 2 == 0:

                # 자막 xml 생성
                str6 = "<generatoritem id=\"Outline Text1\"><name>Outline Text</name><rate><timebase>60</timebase><ntsc>false</ntsc></rate><start>"
                start_time = str(timeCnt)
                str8 = "</start><end>"
                end_time = str(int(timeCnt) + int(dict_audio_size[str(int(lineCnt_subtitle / 2) + 1)]))
                str10 = "</end><in>"
                # start_time
                str12 = "</in><out>"
                # end_time
                str14 = "</out><enabled>true</enabled><anamorphic>false</anamorphic><alphatype>black</alphatype><masterclipid>Outline Text1</masterclipid><effect><name>Outline Text</name><effectid>Outline Text</effectid><effectcategory>Text</effectcategory><effecttype>generator</effecttype><mediatype>video</mediatype><parameter><parameterid>part1</parameterid><name>Text Settings</name><value/></parameter><parameter><parameterid>str</parameterid><name>Text</name><value>"
                text = line
                str16 = "</value></parameter><parameter><parameterid>font</parameterid><name>Font</name><value>BMDoHyeon</value></parameter><parameter><parameterid>style</parameterid><name>Style</name><valuemin>1</valuemin><valuemax>1</valuemax><valuelist><valueentry><name>Regular</name><value>1</value></valueentry></valuelist><value>1</value></parameter><parameter><parameterid>align</parameterid><name>Alignment</name><valuemin>1</valuemin><valuemax>3</valuemax><valuelist><valueentry><name>Left</name><value>1</value></valueentry><valueentry><name>Center</name><value>2</value></valueentry><valueentry><name>Right</name><value>3</value></valueentry></valuelist><value>2</value></parameter><parameter><parameterid>size</parameterid><name>Size</name><valuemin>0</valuemin><valuemax>200</valuemax><value>25</value></parameter><parameter><parameterid>track</parameterid><name>Tracking</name><valuemin>0</valuemin><valuemax>100</valuemax><value>1</value></parameter><parameter><parameterid>lead</parameterid><name>Leading</name><valuemin>-100</valuemin><valuemax>100</valuemax><value>0</value></parameter><parameter><parameterid>aspect</parameterid><name>Aspect</name><valuemin>0</valuemin><valuemax>4</valuemax><value>1</value></parameter><parameter><parameterid>linewidth</parameterid><name>Line Width</name><valuemin>0</valuemin><valuemax>200</valuemax><value>2</value></parameter><parameter><parameterid>linesoft</parameterid><name>Line Softness</name><valuemin>0</valuemin><valuemax>100</valuemax><value>5</value></parameter><parameter><parameterid>textopacity</parameterid><name>Text Opacity</name><valuemin>0</valuemin><valuemax>100</valuemax><value>100</value></parameter><parameter><parameterid>center</parameterid><name>Center</name><value><horiz>0.003</horiz><vert>0.351</vert></value></parameter><parameter><parameterid>textcolor</parameterid><name>Text Color</name><value><alpha>255</alpha><red>0</red><green>0</green><blue>0</blue></value></parameter><parameter><parameterid>supertext</parameterid><name>Text Graphic</name></parameter><parameter><parameterid>superline</parameterid><name>Line Graphic</name></parameter><parameter><parameterid>part2</parameterid><name>Background Settings</name><value/></parameter><parameter><parameterid>xscale</parameterid><name>Horizontal Size</name><valuemin>0</valuemin><valuemax>200</valuemax><value>0</value></parameter><parameter><parameterid>yscale</parameterid><name>Vertical Size</name><valuemin>0</valuemin><valuemax>200</valuemax><value>0</value></parameter><parameter><parameterid>xoffset</parameterid><name>Horizontal Offset</name><valuemin>-100</valuemin><valuemax>100</valuemax><value>0</value></parameter><parameter><parameterid>yoffset</parameterid><name>Vertical Offset</name><valuemin>-100</valuemin><valuemax>100</valuemax><value>0</value></parameter><parameter><parameterid>backsoft</parameterid><name>Back Soft</name><valuemin>0</valuemin><valuemax>100</valuemax><value>0</value></parameter><parameter><parameterid>backopacity</parameterid><name>Back Opacity</name><valuemin>0</valuemin><valuemax>100</valuemax><value>50</value></parameter><parameter><parameterid>backcolor</parameterid><name>Back Color</name><value><alpha>255</alpha><red>255</red><green>255</green><blue>255</blue></value></parameter><parameter><parameterid>superback</parameterid><name>Back Graphic</name></parameter><parameter><parameterid>crop</parameterid><name>Crop</name><value>false</value></parameter><parameter><parameterid>autokern</parameterid><name>Auto Kerning</name><value>true</value></parameter></effect><sourcetrack><mediatype>video</mediatype><trackindex>1</trackindex></sourcetrack></generatoritem>"

                result_subtitle_line1 += str6 + start_time + str8 + end_time + str10 + start_time + str12 + end_time + str14 + text + str16

            else:
                # 자막 xml 생성
                str6_2 = "<generatoritem id=\"Outline Text1\"><name>Outline Text</name><rate><timebase>60</timebase><ntsc>false</ntsc></rate><start>"
                start_time_2 = str(timeCnt)
                str8_2 = "</start><end>"
                end_time_2 = str(int(timeCnt) + dict_audio_size[str(int(lineCnt_subtitle / 2) + 1)])
                str10_2 = "</end><in>"
                # start_time
                str12_2 = "</in><out>"
                # end_time
                str14_2 = "</out><enabled>true</enabled><anamorphic>false</anamorphic><alphatype>black</alphatype><masterclipid>Outline Text1</masterclipid><effect><name>Outline Text</name><effectid>Outline Text</effectid><effectcategory>Text</effectcategory><effecttype>generator</effecttype><mediatype>video</mediatype><parameter><parameterid>part1</parameterid><name>Text Settings</name><value/></parameter><parameter><parameterid>str</parameterid><name>Text</name><value>"
                text_2 = line
                str16_2 = "</value></parameter><parameter><parameterid>font</parameterid><name>Font</name><value>BMDoHyeon</value></parameter><parameter><parameterid>style</parameterid><name>Style</name><valuemin>1</valuemin><valuemax>1</valuemax><valuelist><valueentry><name>Regular</name><value>1</value></valueentry></valuelist><value>1</value></parameter><parameter><parameterid>align</parameterid><name>Alignment</name><valuemin>1</valuemin><valuemax>3</valuemax><valuelist><valueentry><name>Left</name><value>1</value></valueentry><valueentry><name>Center</name><value>2</value></valueentry><valueentry><name>Right</name><value>3</value></valueentry></valuelist><value>2</value></parameter><parameter><parameterid>size</parameterid><name>Size</name><valuemin>0</valuemin><valuemax>200</valuemax><value>25</value></parameter><parameter><parameterid>track</parameterid><name>Tracking</name><valuemin>0</valuemin><valuemax>100</valuemax><value>1</value></parameter><parameter><parameterid>lead</parameterid><name>Leading</name><valuemin>-100</valuemin><valuemax>100</valuemax><value>0</value></parameter><parameter><parameterid>aspect</parameterid><name>Aspect</name><valuemin>0</valuemin><valuemax>4</valuemax><value>1</value></parameter><parameter><parameterid>linewidth</parameterid><name>Line Width</name><valuemin>0</valuemin><valuemax>200</valuemax><value>2</value></parameter><parameter><parameterid>linesoft</parameterid><name>Line Softness</name><valuemin>0</valuemin><valuemax>100</valuemax><value>5</value></parameter><parameter><parameterid>textopacity</parameterid><name>Text Opacity</name><valuemin>0</valuemin><valuemax>100</valuemax><value>100</value></parameter><parameter><parameterid>center</parameterid><name>Center</name><value><horiz>0.003</horiz><vert>0.421</vert></value></parameter><parameter><parameterid>textcolor</parameterid><name>Text Color</name><value><alpha>255</alpha><red>0</red><green>0</green><blue>0</blue></value></parameter><parameter><parameterid>supertext</parameterid><name>Text Graphic</name></parameter><parameter><parameterid>superline</parameterid><name>Line Graphic</name></parameter><parameter><parameterid>part2</parameterid><name>Background Settings</name><value/></parameter><parameter><parameterid>xscale</parameterid><name>Horizontal Size</name><valuemin>0</valuemin><valuemax>200</valuemax><value>0</value></parameter><parameter><parameterid>yscale</parameterid><name>Vertical Size</name><valuemin>0</valuemin><valuemax>200</valuemax><value>0</value></parameter><parameter><parameterid>xoffset</parameterid><name>Horizontal Offset</name><valuemin>-100</valuemin><valuemax>100</valuemax><value>0</value></parameter><parameter><parameterid>yoffset</parameterid><name>Vertical Offset</name><valuemin>-100</valuemin><valuemax>100</valuemax><value>0</value></parameter><parameter><parameterid>backsoft</parameterid><name>Back Soft</name><valuemin>0</valuemin><valuemax>100</valuemax><value>0</value></parameter><parameter><parameterid>backopacity</parameterid><name>Back Opacity</name><valuemin>0</valuemin><valuemax>100</valuemax><value>50</value></parameter><parameter><parameterid>backcolor</parameterid><name>Back Color</name><value><alpha>255</alpha><red>255</red><green>255</green><blue>255</blue></value></parameter><parameter><parameterid>superback</parameterid><name>Back Graphic</name></parameter><parameter><parameterid>crop</parameterid><name>Crop</name><value>false</value></parameter><parameter><parameterid>autokern</parameterid><name>Auto Kerning</name><value>true</value></parameter></effect><sourcetrack><mediatype>video</mediatype><trackindex>1</trackindex></sourcetrack></generatoritem>"

                result_subtitle_line2 += str6_2 + start_time_2 + str8_2 + end_time_2 + str10_2 + start_time_2 + str12_2 + end_time_2 + str14_2 + text_2 + str16_2
                timeCnt += dict_audio_size[str(int(lineCnt_subtitle / 2) + 1)]

            lineCnt_subtitle += 1


    ############# 배경 이미지 넣기 ###############
    result_subtitle_bg += '<track><clipitem><name>subtitle_bg.png</name><enabled>TRUE</enabled><rate><timebase>30</timebase><ntsc>TRUE</ntsc></rate><start>0</start><end>'
    result_subtitle_bg += str(audio_size_sum) + '</end><in>0</in><out>'
    result_subtitle_bg += str(audio_size_sum) + '</out><file id="file-subtitle-bg"><name>subtitle_bg.png</name><pathurl>subtitle_bg.png</pathurl><rate><timebase>30</timebase><ntsc>TRUE</ntsc></rate><media><video><samplecharacteristics><rate><timebase>30</timebase><ntsc>TRUE</ntsc></rate><width>1921</width><height>1080</height><anamorphic>FALSE</anamorphic><pixelaspectratio>square</pixelaspectratio><fielddominance>none</fielddominance></samplecharacteristics></video></media></file><filter><effect><name>Basic Motion</name><effectid>basic</effectid><effectcategory>motion</effectcategory><effecttype>motion</effecttype><mediatype>video</mediatype><pproBypass>false</pproBypass><parameter authoringApp="PremierePro"><parameterid>center</parameterid><name>Center</name><value><horiz>0</horiz><vert>0.0185185</vert></value></parameter></effect></filter></clipitem><enabled>TRUE</enabled><locked>FALSE</locked></track>'
    shutil.copy(urllib.parse.unquote(baseResourcePath + 'subtitle_bg.png'), downloadPath)

    ############# 로고 이미지 넣기 ###############
    result_image_logo += '<track><clipitem><name>logo.png</name><enabled>TRUE</enabled><rate><timebase>30</timebase><ntsc>TRUE</ntsc></rate><start>0</start><end>'
    result_image_logo += str(audio_size_sum) + '</end><in>0</in><out>'
    result_image_logo += str(audio_size_sum) + '</out><file id="file-logo"><name>logo.png</name><pathurl>logo.png</pathurl><rate><timebase>30</timebase><ntsc>TRUE</ntsc></rate><media><video><samplecharacteristics><rate><timebase>30</timebase><ntsc>TRUE</ntsc></rate><width>842</width><height>596</height><anamorphic>FALSE</anamorphic><pixelaspectratio>square</pixelaspectratio><fielddominance>none</fielddominance></samplecharacteristics></video></media></file><filter><effect><name>Basic Motion</name><effectid>basic</effectid><effectcategory>motion</effectcategory><effecttype>motion</effecttype><mediatype>video</mediatype><pproBypass>false</pproBypass><parameter authoringApp="PremierePro"><parameterid>scale</parameterid><name>Scale</name><valuemin>0</valuemin><valuemax>1000</valuemax><value>26</value></parameter><parameter authoringApp="PremierePro"><parameterid>rotation</parameterid><name>Rotation</name><valuemin>-8640</valuemin><valuemax>8640</valuemax><value>0</value></parameter><parameter authoringApp="PremierePro"><parameterid>center</parameterid><name>Center</name><value><horiz>0.961995</horiz><vert>-0.657718</vert></value></parameter><parameter authoringApp="PremierePro"><parameterid>centerOffset</parameterid><name>Anchor Point</name><value><horiz>0</horiz><vert>0</vert></value></parameter><parameter authoringApp="PremierePro"><parameterid>antiflicker</parameterid><name>Anti-flicker Filter</name><valuemin>0.0</valuemin><valuemax>1.0</valuemax><value>0</value></parameter></effect></filter></clipitem><enabled>TRUE</enabled><locked>FALSE</locked></track>'
    shutil.copy(urllib.parse.unquote(baseResourcePath + 'logo.png'), downloadPath)

    slack.send_slack('[automake_video] 자막,배경,로고 작업 완료')

    ############# 문장별 키워드 추출 ###############

    okja = []
    # 1. 이전 포스트에서 크롤링한 댓글파일을 읽기전용으로 호출함
    for line in str(output).split('\n'):
        okja.append(line)

    # 3. 트윗터 패키지 안에 konlpy 모듈호출
    from konlpy.tag import Twitter
    twitter = Twitter()

    # 4. 각 문장별로 형태소 구분하기
    sentences_tag = []
    for sentence in okja:
        morph = twitter.pos(sentence)
        sentences_tag.append(morph)
        #print(morph)
        #print('-' * 30)

    # for sentence in sentences_tag:
    #     print(sentence)
    #     print('-' * 30)

    #print(len(sentences_tag))
    #print('\n' * 3)

    # 5. 명사 혹은 형용사인 품사만 선별해 리스트에 담기
    noun_adj_list = {}


    #print(len(sentences_tag))
    #print((len(sentences_tag) + 1) / 2)

    cnt = 1
    word_sum = ''
    while cnt < (len(sentences_tag)+1):
        if cnt % 2 == 0:
            for word, tag in sentences_tag[cnt-1]:
                if tag in ['Noun', 'Adjective']:
                    try:
                        val = sorted_dict[word]
                        if val is not None:
                            #print(key, k)
                            word_sum += val + '|'
                    except KeyError:
                        a = 1

            noun_adj_list[str(int(cnt/2))] = word_sum
            #print(str(int(cnt/2)))
            #print(cnt, word_sum)
            word_sum = ''
        else:
            for word, tag in sentences_tag[cnt-1]:
                if tag in ['Noun', 'Adjective']:
                    try:
                        val = sorted_dict[word]
                        if val is not None:
                            # print(key, k)
                            word_sum += val + '|'
                    except KeyError:
                        a = 1
            #print(cnt, word_sum)

        cnt = cnt + 1

    ## 라인별 명사 키워드 출력
    # for key, value in noun_adj_list.items():
    #     print(key, value)

    slack.send_slack('[automake_video] 라인별 키워드 추출 완료')

    # 영상 다운로드 , 영상 xml 만들기 #
    ## 영상 xml 만들기 위함 ##

    time_sum = audio_size_sum  # 추후 오디오 파일 길이를 모두 합친길이가 되어야함

    ## line 1 ##
    str1 = "<?xml version=\"1.0\" encoding=\"utf-8\"?><xmeml version=\"5\"><sequence id=\"video\"><name>"
    name = "video_layer_" + question_id
    str3 = "</name><duration>"
    str5 = "</duration><rate><timebase>60</timebase><ntsc>false</ntsc></rate><media><video><format><samplecharacteristics><width>1920</width><height>1080</height><anamorphic>false</anamorphic><pixelaspectratio>square</pixelaspectratio><fielddominance>none</fielddominance></samplecharacteristics></format>"
    str5 += "<track>"
    result = str1 + name + str3 + str(time_sum) + str5
    ## 영상 xml 만들기 위함 ##

    ###############################################

    st_time = 0
    ed_time = 0
    for key, value in noun_adj_list.items():
        pick = ''
        #print(key, value)
        if value == '' or value is None:
            pick = default_keyword
            #print(key, pick)
        else:
            split_value = value.split('|')
            onepick_list = []
            for k in split_value:
                if k != '' and k is not None:
                    onepick_list.append(k)
                    #print(key, k)
            pick = random_pop(onepick_list)

        getUploadListForKeyword = []
        if pick:
            getUploadListForKeyword = tag_list.filter(
                Q(tag__icontains=pick)
            ).distinct()

        urlpick_list = []
        resourcePath = 'C:/projects/djangobook-master/media'
        for list in getUploadListForKeyword:
            #print(list.id, list.tag, list.filepath)
            urlpick_list.append(resourcePath + '/' + str(list.filepath))


        # 영상 xml 생성 시작 #
        line_num = key
        img_num = '1'
        download_url = random_pop(urlpick_list)

        print(key, pick, download_url)

        if download_url.find('/media/upload_file/') > -1:
            print(line_num, download_url)
            #resourcePath = 'C:\projects\djangobook-master'
            download_url_path = urllib.parse.unquote(download_url)
            #download_url_path = resourcePath + download_url_path
            print('media local file copy : ' + download_url_path)

            ## 로컬드라이브에서 -> 정해진위치에 파일 복사 ##
            if os.path.isfile(download_url_path):
                shutil.copy(download_url_path, downloadPath)
            else:
                try:
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
                      downloadPath + str(line_num) + '_' + str(img_num) + '.' + filename_2)

            # 이미지, 영상 해상도 확인 - start #
            from PIL import Image
            width = 1920
            height = 1080
            length = 0
            fps = 0
            try:
                image1 = Image.open(downloadPath + line_num + '_' + img_num + '.' + filename_2)
                width, height = image1.size
                print('image size', width, ',', height)
            except IOError:
                import cv2
                videoObj = cv2.VideoCapture(downloadPath + line_num + '_' + img_num + '.' + filename_2)
                width = int(videoObj.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(videoObj.get(cv2.CAP_PROP_FRAME_HEIGHT))
                length = int(videoObj.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = videoObj.get(cv2.CAP_PROP_FPS)  # Gets the frames per second
                print('video size', width, ',', height)
                print('length : ', length)
                print('fps : ', fps)
                print('seconds : ', length / fps)

            video_seconds_length = length / fps * 60

            c_width = int(1920 / int(width) * 100)
            c_height = int(1080 / int(height) * 100)
            max = 0
            if c_width > c_height:
                max = c_width
            else:
                max = c_height
            # 이미지, 영상 해상도 확인 - end #

            # start - 받은 영상에 맞게 xml 생성 #
            fileId = str(line_num) + '_' + str(img_num) + '.' + filename_2
            pathurl = str(line_num) + '_' + str(img_num) + '.' + filename_2

            # automake_media_xml(line_num, question_id, fileId, pathurl)

            ## start - 반복 ##
            timeCnt = st_time
            lineCnt_check = 0
            if lineCnt % 2 == 0:
                lineCnt_check = int(lineCnt / 2)
                print("lineCnt_check", lineCnt_check)
            else:
                lineCnt_check = int(lineCnt / 2) + 1
                print("lineCnt_check", lineCnt_check)


            if int(line_num) == 1:
                str6 = "<clipitem><name>" + fileId + "</name><rate><ntsc>TRUE</ntsc><timebase>60</timebase></rate><start>"
                str8 = "</start><end>"
                str10 = "</end><in>"
                # start_time
                str12 = "</in><out>"
                end_time = str(int(timeCnt) + int(dict_audio_size[line_num]))
                str14 = "</out><stillframe>TRUE</stillframe><file id=\"" + fileId + "\"><name>" + fileId + "</name><pathurl>"
                text = pathurl
                str16 = "</pathurl><duration>2</duration><media><video><duration>2</duration><stillframe>TRUE</stillframe><samplecharacteristics><width>720</width><height>480</height></samplecharacteristics></video></media></file>"
                str16 += "<filter><effect><name>Basic Motion</name><effectid>basic</effectid><effectcategory>motion</effectcategory><effecttype>motion</effecttype><mediatype>video</mediatype><pproBypass>false</pproBypass><parameter><parameterid>scale</parameterid><name>Scale</name><valuemin>0</valuemin><valuemax>1000</valuemax><value>" + str(
                    max) + "</value></parameter></effect></filter>"
                str16 += "<sourcetrack><mediatype>video</mediatype><trackindex>1</trackindex></sourcetrack></clipitem>"
                str17 = "<transitionitem><start>"
                str17 += str(end_time)
                str17 += "</start><end>"
                str17 += str(int(end_time) + 30)
                str17 += "</end><alignment>start</alignment><cutPointTicks>0</cutPointTicks><rate><timebase>60</timebase><ntsc>FALSE</ntsc></rate><effect><name>Cross Dissolve</name><effectid>Cross Dissolve</effectid><effectcategory>Dissolve</effectcategory><effecttype>transition</effecttype><mediatype>video</mediatype><wipecode>0</wipecode><wipeaccuracy>100</wipeaccuracy><startratio>0</startratio><endratio>1</endratio><reverse>FALSE</reverse></effect></transitionitem>"
                result_video += str6 + str(0) + str8 + str(-1) + str10 + str(0) + str12 + end_time + str14 + text + str16 + str17
            elif int(line_num) == int(lineCnt_check):
                str6 = "<clipitem><name>" + fileId + "</name><rate><ntsc>TRUE</ntsc><timebase>60</timebase></rate><mediadelay>" + str(
                    timeCnt) + "</mediadelay><start>"
                start_time = str(timeCnt)
                str8 = "</start><end>"
                end_time = str(int(timeCnt) + int(dict_audio_size[line_num]))
                str10 = "</end><in>"
                # start_time
                str12 = "</in><out>"
                # end_time
                str14 = "</out><stillframe>TRUE</stillframe><file id=\"" + fileId + "\"><name>" + fileId + "</name><pathurl>"
                text = pathurl
                str16 = "</pathurl><duration>2</duration><media><video><duration>2</duration><stillframe>TRUE</stillframe><samplecharacteristics><width>720</width><height>480</height></samplecharacteristics></video></media></file>"
                str16 += "<filter><effect><name>Basic Motion</name><effectid>basic</effectid><effectcategory>motion</effectcategory><effecttype>motion</effecttype><mediatype>video</mediatype><pproBypass>false</pproBypass><parameter><parameterid>scale</parameterid><name>Scale</name><valuemin>0</valuemin><valuemax>1000</valuemax><value>" + str(
                    max) + "</value></parameter></effect></filter>"
                str16 += "<sourcetrack><mediatype>video</mediatype><trackindex>1</trackindex></sourcetrack></clipitem>"
                result_video += str6 + start_time + str8 + end_time + str10 + start_time + str12 + end_time + str14 + text + str16
            else:
                # 오디오 길이가 더 길때 ( 비디오가 짧을때 )
                if int(video_seconds_length) < int(dict_audio_size[line_num]):
                    video_start_time = str(int(timeCnt) + int(video_seconds_length))
                    end_time = str(int(timeCnt) + int(dict_audio_size[line_num]))
                    str6 = "<clipitem><name>" + fileId + "</name><rate><ntsc>TRUE</ntsc><timebase>60</timebase></rate><start>"
                    str8 = "</start><end>"
                    str10 = "</end><in>"
                    str12 = "</in><out>"
                    str14 = "</out><stillframe>TRUE</stillframe><file id=\"" + fileId + "\"><name>" + fileId + "</name><pathurl>"
                    text = pathurl
                    str16 = "</pathurl><duration>2</duration><media><video><duration>2</duration><stillframe>TRUE</stillframe><samplecharacteristics><width>720</width><height>480</height></samplecharacteristics></video></media></file>"
                    str16 += "<filter><effect><name>Basic Motion</name><effectid>basic</effectid><effectcategory>motion</effectcategory><effecttype>motion</effecttype><mediatype>video</mediatype><pproBypass>false</pproBypass><parameter><parameterid>scale</parameterid><name>Scale</name><valuemin>0</valuemin><valuemax>1000</valuemax><value>" + str(
                        max) + "</value></parameter></effect></filter>"
                    str16 += "<sourcetrack><mediatype>video</mediatype><trackindex>1</trackindex></sourcetrack></clipitem>"
                    result_video += str6 + str(-1) + str8 + video_start_time + str10 + str(0) + str12 + video_start_time + str14 + text + str16
                    # 비디오가 부족할때 추가 클립 - start
                    str6 = "<clipitem><name>" + fileId + "</name><rate><ntsc>TRUE</ntsc><timebase>60</timebase></rate><mediadelay>" + video_start_time + "</mediadelay><start>"
                    str8 = "</start><end>"
                    str10 = "</end><in>"
                    str12 = "</in><out>"
                    str14 = "</out><stillframe>TRUE</stillframe><file id=\"" + fileId + "\"><name>" + fileId + "</name><pathurl>"
                    text = pathurl
                    str16 = "</pathurl><duration>2</duration><media><video><duration>2</duration><stillframe>TRUE</stillframe><samplecharacteristics><width>720</width><height>480</height></samplecharacteristics></video></media></file>"
                    str16 += "<filter><effect><name>Basic Motion</name><effectid>basic</effectid><effectcategory>motion</effectcategory><effecttype>motion</effecttype><mediatype>video</mediatype><pproBypass>false</pproBypass><parameter><parameterid>scale</parameterid><name>Scale</name><valuemin>0</valuemin><valuemax>1000</valuemax><value>" + str(
                        max) + "</value></parameter></effect></filter>"
                    str16 += "<sourcetrack><mediatype>video</mediatype><trackindex>1</trackindex></sourcetrack></clipitem>"
                    # 비디오가 부족할때 추가 클립 - end
                    str17 = "<transitionitem><start>"
                    str17 += str(end_time)
                    str17 += "</start><end>"
                    str17 += str(int(end_time) + 30)
                    str17 += "</end><alignment>start</alignment><cutPointTicks>0</cutPointTicks><rate><timebase>60</timebase><ntsc>FALSE</ntsc></rate><effect><name>Cross Dissolve</name><effectid>Cross Dissolve</effectid><effectcategory>Dissolve</effectcategory><effecttype>transition</effecttype><mediatype>video</mediatype><wipecode>0</wipecode><wipeaccuracy>100</wipeaccuracy><startratio>0</startratio><endratio>1</endratio><reverse>FALSE</reverse></effect></transitionitem>"
                    result_video += str6 + video_start_time + str8 + str(-1) + str10 + video_start_time + str12 + end_time + str14 + text + str16 + str17
                else:
                    str6 = "<clipitem><name>" + fileId + "</name><rate><ntsc>TRUE</ntsc><timebase>60</timebase></rate><start>"
                    str8 = "</start><end>"
                    str10 = "</end><in>"
                    str12 = "</in><out>"
                    end_time = str(int(timeCnt) + int(dict_audio_size[line_num]))
                    str14 = "</out><stillframe>TRUE</stillframe><file id=\"" + fileId + "\"><name>" + fileId + "</name><pathurl>"
                    text = pathurl
                    str16 = "</pathurl><duration>2</duration><media><video><duration>2</duration><stillframe>TRUE</stillframe><samplecharacteristics><width>720</width><height>480</height></samplecharacteristics></video></media></file>"
                    str16 += "<filter><effect><name>Basic Motion</name><effectid>basic</effectid><effectcategory>motion</effectcategory><effecttype>motion</effecttype><mediatype>video</mediatype><pproBypass>false</pproBypass><parameter><parameterid>scale</parameterid><name>Scale</name><valuemin>0</valuemin><valuemax>1000</valuemax><value>" + str(
                        max) + "</value></parameter></effect></filter>"
                    str16 += "<sourcetrack><mediatype>video</mediatype><trackindex>1</trackindex></sourcetrack></clipitem>"
                    str17 = "<transitionitem><start>"
                    str17 += str(end_time)
                    str17 += "</start><end>"
                    str17 += str(int(end_time) + 30)
                    str17 += "</end><alignment>start</alignment><cutPointTicks>0</cutPointTicks><rate><timebase>60</timebase><ntsc>FALSE</ntsc></rate><effect><name>Cross Dissolve</name><effectid>Cross Dissolve</effectid><effectcategory>Dissolve</effectcategory><effecttype>transition</effecttype><mediatype>video</mediatype><wipecode>0</wipecode><wipeaccuracy>100</wipeaccuracy><startratio>0</startratio><endratio>1</endratio><reverse>FALSE</reverse></effect></transitionitem>"
                    result_video += str6 + str(-1) + str8 + str(-1) + str10 + str(0) + str12 + end_time + str14 + text + str16 + str17

            # str6 = "<clipitem><name>" + fileId + "</name><rate><ntsc>TRUE</ntsc><timebase>60</timebase></rate><mediadelay>" + str(
            #     timeCnt) + "</mediadelay><start>"
            # start_time = str(timeCnt)
            # str8 = "</start><end>"
            # end_time = str(int(timeCnt) + int(dict_audio_size[line_num]))
            # str10 = "</end><in>"
            # # start_time
            # str12 = "</in><out>"
            # # end_time
            # str14 = "</out><stillframe>TRUE</stillframe><file id=\"" + fileId + "\"><name>" + fileId + "</name><pathurl>"
            # text = pathurl
            # str16 = "</pathurl><duration>2</duration><media><video><duration>2</duration><stillframe>TRUE</stillframe><samplecharacteristics><width>720</width><height>480</height></samplecharacteristics></video></media></file>"
            # str16 += "<filter><effect><name>Basic Motion</name><effectid>basic</effectid><effectcategory>motion</effectcategory><effecttype>motion</effecttype><mediatype>video</mediatype><pproBypass>false</pproBypass><parameter><parameterid>scale</parameterid><name>Scale</name><valuemin>0</valuemin><valuemax>1000</valuemax><value>" + str(
            #     max) + "</value></parameter></effect></filter>"
            # str16 += "<sourcetrack><mediatype>video</mediatype><trackindex>1</trackindex></sourcetrack></clipitem>"
            # result_video += str6 + start_time + str8 + end_time + str10 + start_time + str12 + end_time + str14 + text + str16

            # 오디오 track 만들기 #
            audio_filename = "voice_" + str(line_num) + ".mp3"
            a_str1 = "<clipitem><name>" + audio_filename
            a_str2 = "</name><enabled>TRUE</enabled><rate><timebase>60</timebase><ntsc>FALSE</ntsc></rate><start>"
            # start_time
            a_str4 = "</start><end>"
            # end_time
            a_str6 = "</end><in>0</in><out>"
            # dict_audio_size[line_num]
            a_str8 = "</out><file id=\"file-a" + line_num + "\"><name>" + audio_filename + "</name><pathurl>"
            a_str10 = "</pathurl><rate><timebase>30</timebase><ntsc>TRUE</ntsc></rate><media><audio><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics><channelcount>1</channelcount><audiochannel><sourcechannel>1</sourcechannel></audiochannel></audio></media></file><sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack><filter><effect><name>Audio Levels</name><effectid>audiolevels</effectid><effectcategory>audiolevels</effectcategory><effecttype>audiolevels</effecttype><mediatype>audio</mediatype><pproBypass>false</pproBypass><parameter authoringApp=\"PremierePro\"><parameterid>level</parameterid><name>Level</name><valuemin>0</valuemin><valuemax>3.98109</valuemax><value>2</value></parameter></effect></filter></clipitem>"
            result_audio_voice += a_str1 + a_str2 + str(timeCnt) + a_str4 + str(int(timeCnt) + int(dict_audio_size[line_num])) + a_str6 + str(dict_audio_size[line_num]) + a_str8 + audio_filename + a_str10

            st_time = end_time
            ## end- 반복 ##
            # end - 받은 영상에 맞게 xml 생성 #

    result_audio_bg += '<track><clipitem><name>bg_2.mp3</name><enabled>TRUE</enabled><rate><timebase>60</timebase><ntsc>FALSE</ntsc></rate><start>0</start><end>' + str(audio_size_sum)
    result_audio_bg += '</end><in>0</in><out>' + str(audio_size_sum)
    result_audio_bg += '</out><file id="file-bgm"><name>bg_2.mp3</name><pathurl>bg_2.mp3</pathurl><rate><timebase>30</timebase><ntsc>TRUE</ntsc></rate><media><audio><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics><channelcount>1</channelcount><audiochannel><sourcechannel>1</sourcechannel></audiochannel></audio></media></file><sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack><filter><effect><name>Audio Levels</name><effectid>audiolevels</effectid><effectcategory>audiolevels</effectcategory><effecttype>audiolevels</effecttype><mediatype>audio</mediatype><pproBypass>false</pproBypass><parameter authoringApp="PremierePro"><parameterid>level</parameterid><name>Level</name><valuemin>0</valuemin><valuemax>3.98109</valuemax><value>1</value></parameter></effect></filter></clipitem><enabled>TRUE</enabled><locked>FALSE</locked><outputchannelindex>1</outputchannelindex></track>'
    shutil.copy(urllib.parse.unquote(baseResourcePath + 'bg_2.mp3'), downloadPath)

    ## 영상 xml 만들기 ##

    result += result_video
    result += "</track>"
    result += result_image
    result += result_image_logo
    result += result_subtitle_bg
    result += "<track>"
    result += result_subtitle_line2
    result += "</track><track>"
    result += result_subtitle_line1
    result += "</track>"
    result += "</video>"
    # 비디오 끝

    # 오디오 시작
    result += "<audio><format><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics></format><outputs><group><index>1</index><numchannels>1</numchannels><downmix>0</downmix><channel><index>1</index></channel></group></outputs>"
    result += "<track>"
    result += result_audio_voice
    result += "<enabled>TRUE</enabled><locked>FALSE</locked><outputchannelindex>1</outputchannelindex></track>"
    result += result_audio_bg
    result += "</audio>"
    # 오디오 끝

    result += "</media></sequence></xmeml>"
    writexml = open(downloadPath + '완료_' + question_id + '.xml', 'w', encoding="utf-8")
    writexml.write(result)
    writexml.close()

    slack.send_slack('[automake_video] 영상 추출 완료')

    """
    파일 다운로드 받기 
    참고 : https://parkhyeonchae.github.io/2020/04/12/django-project-24/
    """
    ## 영상 xml 만들기 ##

    file_list = os.listdir(downloadPath)
    # for list in file_list:
    #     print(list)

    # with zipfile.ZipFile(downloadPath + 'keyword.zip', 'w', compression=zipfile.ZIP_DEFLATED) as new_zip:
    with zipfile.ZipFile('./static/output_2/' + 'keyword_' + question_id + '.zip', 'w') as new_zip:
        for list in file_list:
            #print(list)
            new_zip.write(downloadPath + list, arcname=list)

    slack.send_slack('[automake_video] zip 파일 생성 완료')
    automake_modify_download_true(question_id)


    # 프리미어프로 -> 영상 인코딩하기
    slack.send_slack('[automake_video] 비디오 인코딩 시작')
    run_video_encoding(question_id)
    slack.send_slack('[automake_video] 비디오 인코딩 완료')

    filepath = './static/output_2/video_layer_' + question_id + '.mp4'

    slack.send_slack('[automake_video] 유튜브 동영상 업로드 시작')
    import subprocess
    # run your program and collect the string output
    cmd = [
        'python',
        'upload_video_sst.py',
        "--file=" + filepath,
        "--title=" + question.subject,
        "--description=안녕하세요. 여러분들이 꼭 알아야하는 뉴스만 제대로 전해드리는 시사통 입니다.",
        "--keywords=지식,뉴스,한국,중국,일본,미국,문재인,아베,스가,시진핑,바이든,쓸모왕,Travel Tube,퍼플튜브,깡통튜브,잡식왕",
        "--category=25",
        "--privacyStatus=private"
    ]
    out_str = subprocess.Popen(cmd, shell=True, stdin=None, stdout=None, stderr=None, close_fds=True,
                               creationflags=subprocess.DETACHED_PROCESS)
    #out_str = subprocess.check_output(cmd, shell=True)

    print(out_str)
    slack.send_slack('[automake_video] 유튜브 동영상 업로드 완료')

    automake_youtube_upload_true(question_id)


    noun_adj_list = json.dumps(noun_adj_list,ensure_ascii=False)
    return HttpResponse(noun_adj_list, content_type="application/json")

def run_video_encoding(qid):
    import pyautogui
    import time

    pyautogui.position()
    # 사용 예시
    x, y = pyautogui.position()
    print("x={0},y={1}".format(x, y))

    pyautogui.hotkey('win', 'd')
    pyautogui.moveTo(2511, 36, 1)
    pyautogui.click(clicks=2)


    time.sleep(30)
    slack.send_slack('[automake_video] 프리미어프로 실행')
    pyautogui.hotkey('ctrl', 'i')

    time.sleep(5)

    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)

    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.typewrite('C:/projects/djangobook-master/static/keyword_2/'+qid)
    time.sleep(1)

    pyautogui.press('enter')

    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)

    pyautogui.press('pagedown')
    pyautogui.press('pagedown')
    pyautogui.press('pagedown')
    pyautogui.press('pagedown')
    pyautogui.press('pagedown')
    pyautogui.press('pagedown')
    pyautogui.press('pagedown')

    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(120)
    slack.send_slack('[automake_video] 완료 xml 불러오기')
    pyautogui.moveTo(106, 828, 1)
    pyautogui.click()
    time.sleep(1)

    pyautogui.typewrite('video_layer')
    time.sleep(1)

    pyautogui.moveTo(115, 902, 1)
    pyautogui.click(clicks=2)
    time.sleep(10)

    pyautogui.hotkey('ctrl', 'm')
    time.sleep(10)

    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)

    pyautogui.press('space')
    time.sleep(5)

    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)

    pyautogui.press('enter')
    time.sleep(5)

    pyautogui.typewrite('C:/projects/djangobook-master/static/output_2')
    time.sleep(1)

    pyautogui.press('enter')
    time.sleep(5)
    pyautogui.hotkey('alt', 's')
    time.sleep(5)

    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)
    pyautogui.press('tab')
    time.sleep(1)

    pyautogui.press('space')
    time.sleep(360)

    pyautogui.moveTo(2533, 9, 1)
    pyautogui.click()
    time.sleep(1)
    pyautogui.moveTo(1323, 726, 1)
    pyautogui.click()
    time.sleep(5)



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