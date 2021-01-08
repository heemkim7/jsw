from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime

from ..models import Upload
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
            return redirect('pybo:upload_list')
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
    print(upload_id)
    print(upload.tag)
    print(upload.filepath)

    if request.method == "POST":
        form = UploadForm(request.POST, instance=upload)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.author = request.user
            upload.modify_date = timezone.now()  # 수정일시 저장
            upload.save()
            return redirect('pybo:upload_list')
    else:
        form = UploadForm(instance=upload)
        form.id = upload.id
        form.author = upload.author
        form.subject = upload.subject
        form.create_date = upload.create_date
        form.modify_date = upload.modify_date
        form.filefolder = upload.filefolder
        form.filename = upload.filename
    context = {'form': form}

    return render(request, 'pybo/upload_form.html', context)


@login_required(login_url='common:login')
def upload_delete(request):
    """
    파일업로드 삭제
    """

    if request.method == 'POST':
        upload_id = request.POST.get('upload_id', '')
        upload = get_object_or_404(Upload, pk=upload_id)

        print("[UPLOAD_DELETE] upload.id : " + upload_id)
        print("[UPLOAD_DELETE] upload.tag : " + upload.tag)

        resourcePath = 'C:/projects/djangobook-master/media'
        print("[UPLOAD_DELETE] file : " + resourcePath + '/' + str(upload.filepath))
        os.remove(resourcePath + '/' + str(upload.filepath))
        print("[UPLOAD_DELETE] thumbnail " + resourcePath + '/' + str(upload.filepath))
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
    paginator = Paginator(upload_list, 96)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context = {'upload_list': page_obj, 'page': page, 'kw': kw, 'distinct_tag_list': distinct_tag_list}
    return render(request, 'pybo/upload_search_keyword.html', context)




@login_required(login_url='common:login')
def upload_tag_list(request):
    tag_list = []







    #slack = Slacker('xoxb-1615709181554-1615920445683-0Jq0kIhfrquKmSz6izJ4okgj')

    # Send a message to #general channel
    #slack.chat.post_message('#jsw', 'jsw test!')

    context = {'tag_list': tag_list}
    return render(request, 'pybo/upload_taglist.html', context)