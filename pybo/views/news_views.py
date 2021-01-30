from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime

from ..models import Upload
from pybo.forms import UploadForm

import cv2

@login_required(login_url='common:login')
def news_list(request):
    """
    파일업로드 태그 목록 출력
    """

    upload_list = Upload.objects.all()
    tag_list = []

    for list in upload_list:
        ##print(list.tag)
        tags = list.tag.split(',')
        for tag in tags:
            if tag not in tag_list:
                tag_list.append(tag)

    tag_list.sort()

    context = {'tag_list': tag_list}
    return render(request, 'pybo/news_list.html', context)