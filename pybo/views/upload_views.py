from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime
from django.http import HttpResponse
import json

from ..models import Upload, Keyword
from pybo.forms import UploadForm
import os

import cv2

@login_required(login_url='common:login')
def upload(request):
    """
    파일업로드
    """

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            if request.FILES:
                if 'filepath' in request.FILES.keys():
                    upload.filename = request.FILES['filepath'].name
            upload.author = request.user  # 추가한 속성 author 적용
            upload.create_date = timezone.now()
            upload.save()
            upload.filefolder = get_path()
            upload.filename = str(upload.filepath).replace(upload.filefolder+'/','')
            # upload.filename = str(upload.filename).replace(' ','_')
            # upload.filename = str(upload.filename).replace('(', '')
            # upload.filename = str(upload.filename).replace(')', '')
            print(upload.filefolder)
            print(upload.filename)
            print(upload.filepath)
            upload.save()
            makeStillCutImage('media/'+get_path(), upload.filename, upload.id)
            return redirect('pybo:upload')
    else:
        form = UploadForm()

    context = { 'form' : form}
    return render(request, 'pybo/upload_form.html', context)


def get_path():
    ymd_path = datetime.now().strftime('%Y/%m/%d')
    return '/'.join(['upload_file', ymd_path])


def makeStillCutImage(path, name, id, onlyMainStillCut=False):
    videoObj = cv2.VideoCapture(path+'/'+name)

    seconds = 3
    length = int(videoObj.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(videoObj.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(videoObj.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = videoObj.get(cv2.CAP_PROP_FPS)  # Gets the frames per second

    print('length : ', length)
    print('width : ', width)
    print('height : ', height)
    print('fps : ', fps)
    print('seconds : ', length/fps)

    multiplier = fps * seconds

    frameCount = 0
    ret = 1

    while ret:
        frameId = int(round(videoObj.get(1)))  # current frame number
        ret, frame = videoObj.read()

        if frameId % multiplier < 1:
            # cv2.resize(img, dsize, fx, fy, interpolation)
            if frameCount == 1:
                resizeImage = cv2.resize(frame, (1280, 720))
                print(path)
                cv2.imwrite(path + '/' + str(id) + ".jpg", resizeImage)
                #cv2.imwrite('compress_img1.png', img,  [int(cv2.IMWRITE_PNG_COMPRESSION), 9])
                #cv2.imwrite('./data/Lena2.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 70])
            else:
                print(path)

            frameCount += 1

        if frameCount == 2:
            break

        if onlyMainStillCut:
            break


@login_required(login_url='common:login')
def upload_list(request):
    """
    파일업로드 목록 출력
    """
    # 입력 파라미터
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어

    # 정렬

    upload_list = Upload.objects.order_by('-create_date')

    tag_list = upload_list
    distinct_tag_list = []

    for list in tag_list:
        tags = list.tag.split(',')
        for tag in tags:
            if tag not in distinct_tag_list:
                distinct_tag_list.append(tag)

    distinct_tag_list.sort()
    #print(distinct_tag_list)
    #len(distinct_tag_list)

    # 검색
    if kw:
        upload_list = upload_list.filter(
            Q(subject__icontains=kw) |  # 제목검색
            Q(tag__icontains=kw) |  # 내용검색
            Q(author__username__icontains=kw)  # 질문 글쓴이검색
        ).distinct()

    # 페이징처리
    paginator = Paginator(upload_list, 24)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context = {'upload_list': page_obj, 'page': page, 'kw': kw, 'distinct_tag_list': distinct_tag_list}
    return render(request, 'pybo/upload_list.html', context)


@login_required(login_url='common:login')
def upload_modify(request, upload_id):
    """
    파일업로드 상세페이지 수정
    """
    upload = get_object_or_404(Upload, pk=upload_id)
    print('[upload_modify] upload_id : ' + str(upload_id))
    print('[upload_modify] upload.tag : ' + str(upload.tag))
    print('[upload_modify] upload.filepath : ' + str(upload.filepath))
    print('[upload_modify] request : ' + str(request.META.get('HTTP_REFERER')))
    print('[upload_modify] list_referer : ' + str(request.POST.get('list_referer')))

    if request.method == "POST":
        form = UploadForm(request.POST, instance=upload)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.author = request.user
            upload.modify_date = timezone.now()  # 수정일시 저장
            upload.save()
            #return redirect('pybo:upload_list')
            return redirect(request.POST.get('list_referer'))
    else:
        form = UploadForm(instance=upload)
        form.id = upload.id
        form.author = upload.author
        form.subject = upload.subject
        form.create_date = upload.create_date
        form.modify_date = upload.modify_date
        form.filefolder = upload.filefolder
        form.filename = upload.filename
    context = {'form': form, 'list_referer':request.META.get('HTTP_REFERER') }

    return render(request, 'pybo/upload_form.html', context)


@login_required(login_url='common:login')
def upload_delete(request):
    """
    파일업로드 삭제
    """

    if request.method == 'POST':
        upload_id = request.POST.get('upload_id', '')
        upload = get_object_or_404(Upload, pk=upload_id)

        print("[upload_delete] upload.id : " + str(upload_id))
        print("[upload_delete] upload.tag : " + str(upload.tag))

        resourcePath = 'C:/projects/djangobook-master/media'
        print("[upload_delete] file : " + resourcePath + '/' + str(upload.filepath))
        os.remove(resourcePath + '/' + str(upload.filepath))
        print("[upload_delete] thumbnail : " + resourcePath + '/' + str(upload.filepath))
        os.remove(resourcePath + '/' + str(upload.filefolder) + '/' + str(upload.id) + '.jpg')
        upload.delete()

    return redirect('pybo:upload_list')



@login_required(login_url='common:login')
def upload_search_keyword(request):
    """
    파일업로드 목록 출력
    """
    # 입력 파라미터
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어

    ## 키워드를 dict로 불러옴
    keyword_list = Keyword.objects.order_by('-count')
    dict = {}
    for keyword in keyword_list:
        # print(str(keyword.key) + ' : ' + str(keyword.value))
        if keyword.value is None:
            dict[keyword.key] = keyword.key
        else:
            dict[keyword.key] = keyword.value

    ## kw가 dict에 없을경우 예외처리
    try:
        kw = dict[kw]
    except KeyError:
        kw = kw

    ## 영상검색 태그 리스트 뽑기
    upload_list = Upload.objects.order_by('-create_date')

    tag_list = upload_list
    distinct_tag_list = []

    for list in tag_list:
        tags = list.tag.split(',')
        for tag in tags:
            if tag not in distinct_tag_list:
                distinct_tag_list.append(tag)

    distinct_tag_list.sort()
    #print(distinct_tag_list)
    #len(distinct_tag_list)

    # 검색
    if kw:
        upload_list = upload_list.filter(
            Q(subject__icontains=kw) |  # 제목검색
            Q(tag__icontains=kw) |  # 내용검색
            Q(author__username__icontains=kw)  # 질문 글쓴이검색
        ).distinct()

    # 페이징처리
    paginator = Paginator(upload_list, 96)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context = {'upload_list': page_obj, 'page': page, 'kw': kw, 'distinct_tag_list': distinct_tag_list}
    return render(request, 'pybo/upload_search_keyword.html', context)




@login_required(login_url='common:login')
def upload_keyword_batch(request):
    tag_list = []

    from collections import Counter
    okja = []
    cnt = 1
    # 1. 이전 포스트에서 크롤링한 댓글파일을 읽기전용으로 호출함
    while cnt <= 79:
        file = open('C:\projects\djangobook-master\static\output/a/1 ('+str(cnt)+').txt', 'r', encoding='utf-8')
        lines = file.readlines()

        # 2. 변수 okja에 전체댓글을 다시저장

        for line in lines:
            okja.append(line)
        file.close()
        cnt = cnt + 1

    # 3. 트윗터 패키지 안에 konlpy 모듈호출
    from konlpy.tag import Twitter
    twitter = Twitter()

    # 4. 각 문장별로 형태소 구분하기
    sentences_tag = []
    for sentence in okja:
        morph = twitter.pos(sentence)
        sentences_tag.append(morph)
        print(morph)
        print('-' * 30)

    print(sentences_tag)
    print(len(sentences_tag))
    print('\n' * 3)

    # 5. 명사 혹은 형용사인 품사만 선별해 리스트에 담기
    noun_adj_list = []
    for sentence1 in sentences_tag:
        for word, tag in sentence1:
            if tag in ['Adjective']:
            #if tag not in ['Josa', 'Punctuation', 'Foreign', 'Verb']:
                noun_adj_list.append(word)

    # 6. 선별된 품사별 빈도수 계산 & 상위 빈도 10위 까지 출력
    count = Counter(noun_adj_list)
    print(count.most_common(2000))


    file = open('C:\projects\djangobook-master\static\output/a/Adjective.txt', 'w', encoding='utf-8')
    for key, value in count.most_common(2000):
        file.write(str(key)+'|'+str(value)+'\n')

    file.close()

    from gensim.summarization.summarizer import summarize




    context = {'tag_list': tag_list}
    return render(request, 'pybo/upload_keyword_list.html', context)



@login_required(login_url='common:login')
def upload_keyword_list(request):

    keyword_list = Keyword.objects.order_by('-count')

    context = {'keyword_list': keyword_list}
    return render(request, 'pybo/upload_keyword_list.html', context)


@login_required(login_url='common:login')
def upload_keyword_value_set(request):
    from django.core import serializers

    dict = {}

    # 키워드 리스트
    keyword_list = Keyword.objects.order_by('-count')
    data = serializers.serialize('json', keyword_list)
    for keyword in keyword_list:
        #print(str(keyword.key) + ' : ' + str(keyword.value))
        dict[keyword.key] = keyword.value

    # 영상 태그 리스트
    tag_list = Upload.objects.order_by('-create_date')
    for list in tag_list:
        tags = list.tag.split(',')
        for tag in tags:
            dict[tag] = tag

    sdict = sorted(dict.items(), key = lambda item: len(item[0]), reverse=False)

    sorted_dict = {}
    for key, value in sdict:
        #print(str(key))
        #print(str(value))
        sorted_dict[key] = value

    sorted_dict = json.dumps(sorted_dict,ensure_ascii=False)

    return HttpResponse(sorted_dict, content_type="application/json")


@login_required(login_url='common:login')
def upload_keyword_create(request):
    """
    키워드 등록
    """

    if request.method == 'POST':
        keyword_id = request.POST.get('keyword_id', '')
        key = request.POST.get('key', '')
        value = request.POST.get('value', '')
        if keyword_id == '':
            keyword = Keyword()
            keyword.count = 0
            keyword.key = key
            keyword.value = value
            keyword.create_date = timezone.now()
            print("[keyword_create] keyword_id : " + str(keyword_id) + ' | keyword.key : ' + str(
                key) + ' | keyword.value : ' + str(value))
            keyword.save()
            context = {'status': 'create', 'keyword_id': keyword.id}
            return HttpResponse(json.dumps(context), content_type="application/json")


@login_required(login_url='common:login')
def upload_keyword_modify(request):
    """
    키워드 수정
    """

    if request.method == 'POST':
        keyword_id = request.POST.get('keyword_id', '')
        key = request.POST.get('key', '')
        value = request.POST.get('value', '')

        if keyword_id != '':
            keyword = get_object_or_404(Keyword, pk=keyword_id)
            keyword.value = value
            print("[keyword_modify] keyword_id : " + str(keyword_id) + ' | keyword.key : ' + str(
                key) + ' | keyword.value : ' + str(value))
            keyword.save()
            context = {'status': 'modify', 'keyword_id': keyword_id, 'key':key, 'value':value}
            return HttpResponse(json.dumps(context), content_type="application/json")



@login_required(login_url='common:login')
def upload_keyword_delete(request):
    """
    키워드 삭제
    """
    from django.http import HttpResponse
    import json

    if request.method == 'POST':
        keyword_id = request.POST.get('keyword_id', '')
        if keyword_id != '':
            keyword = get_object_or_404(Keyword, pk=keyword_id)
            print("[keyword_delete] keyword_id : " + str(keyword_id) + ' | ' + str(keyword.key) + ' | ' + str(keyword.value))
            keyword.delete()
            context = {'status': 'delete', 'keyword_id': keyword_id}
            return HttpResponse(json.dumps(context), content_type="application/json")

