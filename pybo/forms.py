from django import forms

from pybo.models import Question, Answer, Comment, Upload, Youtube


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['subject', 'content', 'status', 'category']
        labels = {
            'subject': '제목',
            'content': '내용',
            'status': '상태',
            'category': '카테고리',
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        labels = {
            'content': '답변내용',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': '댓글내용',
        }


class UploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ['tag', 'filepath']
        labels = {
            'tag': 'Tags',
            'filepath': 'File Path',
        }


class YoutubeForm(forms.ModelForm):
    class Meta:
        model = Youtube
        fields = ['subject', 'content', 'status', 'category']
        labels = {
            'subject': '제목',
            'content': '내용',
            'status': '상태',
            'category': '카테고리',
        }