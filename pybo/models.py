from django.contrib.auth.models import User
from django.db import models
from uuid import uuid4
from datetime import datetime


class Question(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_question')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    download_flag = models.CharField(null=True, max_length=10, blank=True)
    upload_target = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(User, related_name='voter_question')

    def __str__(self):
        return self.subject


class Answer(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_answer')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(User, related_name='voter_answer')


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE)


class Upload(models.Model):
    def get_file_path(instance, filename):
        ymd_path = datetime.now().strftime('%Y/%m/%d')
        return '/'.join(['upload_file/', ymd_path, filename])

    filepath = models.FileField(upload_to=get_file_path, null=True, blank=True, verbose_name='파일경로')
    filefolder = models.CharField(max_length=1000, null=True, blank=True, verbose_name='파일폴더')
    filename = models.CharField(max_length=255, null=True, blank=True, verbose_name='파일명')
    subject = models.CharField(max_length=200, null=True, verbose_name='제목')

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_upload')
    tag = models.CharField(max_length=200, null=True, verbose_name='태그')
    create_date = models.DateTimeField(null=True)
    modify_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.subject