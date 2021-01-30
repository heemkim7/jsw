from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from datetime import datetime
from django.http import HttpResponse
import json
from ..models import Question
from ..api import slack

@login_required(login_url='common:login')
def upload_youtube(request):
    """
    파일업로드
    """

    if request.method == 'POST':
        if 'filepath' in request.FILES.keys():
            question_id = request.POST.get('question_id')
            question = get_object_or_404(Question, pk=question_id)
            print(question_id, question.subject)
            handle_uploaded_file(request.FILES['filepath'])
            print('/media/youtube_file/jsw/' + request.FILES['filepath'].name)
            filepath = '/media/youtube_file/jsw/' + request.FILES['filepath'].name

            # import subprocess
            # # run your program and collect the string output
            # cmd = [
            #     'python',
            #     'upload_video_jsw.py',
            #     "--file=."+filepath,
            #     "--title="+question.subject,
            #     "--description=본 채널은 연합뉴스 콘텐츠 이용계약을 맺었으며, 연합뉴스는 본 채널의 편집방향과 무관합니다.저작권자(C)연합뉴스, 잡식왕",
            #     "--keywords=뉴스,한국,중국,일본,미국,잡식,문재인,아베,스가,시진핑,바이든",
            #     "--category=25",
            #     "--privacyStatus=private"
            # ]
            # out_str = subprocess.Popen(cmd,shell=True,stdin=None,stdout=None,stderr=None,close_fds=True, creationflags=subprocess.DETACHED_PROCESS)
            # print(out_str)
            upload_youtube_upload_true(question_id)
            slack.send_slack('[upload_youtube] 업로드 완료 : ' + filepath)

    context = {'status': 'complete', 'filepath': filepath}
    return HttpResponse(json.dumps(context), content_type="application/json")


def handle_uploaded_file(f):
    with open('media/youtube_file/jsw/'+f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def upload_youtube_upload_true(question_id):
    """
    pybo 다운로드 완료
    """
    question = get_object_or_404(Question, pk=question_id)
    print(question.status)
    print(question.create_date)
    question.upload_flag = '1'
    question.status = '완료'
    question.save()


def get_path():
    ymd_path = datetime.now().strftime('%Y/%m/%d')
    return '/'.join(['upload_file', ymd_path])