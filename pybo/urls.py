from django.urls import path
from django.conf import settings
from django.conf.urls import url
from django.views.static import serve

from .views import base_views, question_views, editor_views, answer_views, comment_views, vote_views, upload_views, news_views, test_views, upload_youtube_views, automake_views

app_name = 'pybo'

urlpatterns = [
    # base_views.py
    path('', base_views.index, name='index'),
    path('<int:question_id>/', base_views.detail, name='detail'),

    # question_views.py
    path('question/create/', question_views.question_create, name='question_create'),
    path('question/modify/<int:question_id>/', question_views.question_modify, name='question_modify'),
    path('question/delete/<int:question_id>/', question_views.question_delete, name='question_delete'),

    # editor_views.py
    path('editor/', editor_views.editor, name='editor'),
    path('editor/create', editor_views.editor_create, name='editor_create'),
    path('editor/convert', editor_views.editor_convert, name='editor_convert'),
    path('editor/automake/subchannel', editor_views.editor_automake_subchannel, name='editor_automake_subchannel'),
    path('editor/automake', editor_views.editor_automake, name='editor_automake'),
    path('editor/subtitle', editor_views.editor_subtitle, name='editor_subtitle'),
    path('editor/media', editor_views.editor_media_xml, name='editor_media_xml'),
    path('editor/keyword', editor_views.editor_keyword, name='editor_keyword'),
    path('editor/keyword/save', editor_views.editor_keyword_save, name='editor_keyword_save'),
    path('editor/keyword/search', editor_views.editor_keyword_search, name='editor_keyword_search'),
    path('editor/keyword/selectdown', editor_views.editor_keyword_select_download, name='editor_keyword_select_download'),


    # automake_views.py
    path('automake/', automake_views.automake, name='automake'),
    path('automake/<int:question_id>/', automake_views.automake_detail, name='automake_detail'),
    path('automake/editor', automake_views.automake_editor, name='automake_editor'),
    path('automake/create', automake_views.automake_create, name='automake_create'),
    path('automake/modify/<int:question_id>/', automake_views.automake_modify, name='automake_modify'),
    path('automake/delete/<int:question_id>/', automake_views.automake_delete, name='automake_delete'),
    path('automake/save', automake_views.automake_save, name='automake_save'),
    path('automake/convert', automake_views.automake_convert, name='automake_convert'),
    path('automake/video', automake_views.automake_video, name='automake_video'),
    path('automake/youtube_upload_complete', automake_views.automake_youtube_upload_complete, name='automake_youtube_upload_complete'),
    path('automake/create_thumbnail', automake_views.automake_create_thumbnail, name='automake_create_thumbnail'),


    # upload_views.py
    path('upload/', upload_views.upload, name='upload'),
    path('upload/list', upload_views.upload_list, name='upload_list'),
    path('upload/modify/<int:upload_id>/', upload_views.upload_modify, name='upload_modify'),
    path('upload/delete/', upload_views.upload_delete, name='upload_delete'),
    path('upload/search/keyword', upload_views.upload_search_keyword, name='upload_search_keyword'),

    path('upload/keyword/list', upload_views.upload_keyword_list, name='upload_keyword_list'),
    path('upload/keyword/dict', upload_views.upload_keyword_value_set, name='upload_keyword_value_set'),
    path('upload/keyword/create', upload_views.upload_keyword_create, name='upload_keyword_create'),
    path('upload/keyword/modify', upload_views.upload_keyword_modify, name='upload_keyword_modify'),
    path('upload/keyword/delete', upload_views.upload_keyword_delete, name='upload_keyword_delete'),

    # upload_youtube_views.py
    path('upload/youtube', upload_youtube_views.upload_youtube, name='upload_youtube'),

    # news_views.py
    path('news/list', news_views.news_list, name='news_list'),

    # test_views.py
    path('test/', test_views.test, name='test'),
    path('test2/', test_views.test2, name='test2'),
    path('test/start', test_views.test_start, name='test_start'),
    path('test/end', test_views.test_end, name='test_end'),

    # answer_views.py
    path('answer/create/<int:question_id>/', answer_views.answer_create, name='answer_create'),
    path('answer/modify/<int:answer_id>/', answer_views.answer_modify, name='answer_modify'),
    path('answer/delete/<int:answer_id>/', answer_views.answer_delete, name='answer_delete'),

    # comment_views.py
    path('comment/create/question/<int:question_id>/', comment_views.comment_create_question, name='comment_create_question'),
    path('comment/modify/question/<int:comment_id>/', comment_views.comment_modify_question, name='comment_modify_question'),
    path('comment/delete/question/<int:comment_id>/', comment_views.comment_delete_question, name='comment_delete_question'),
    path('comment/create/answer/<int:answer_id>/', comment_views.comment_create_answer, name='comment_create_answer'),
    path('comment/modify/answer/<int:comment_id>/', comment_views.comment_modify_answer, name='comment_modify_answer'),
    path('comment/delete/answer/<int:comment_id>/', comment_views.comment_delete_answer, name='comment_delete_answer'),

    # vote_views.py
    path('vote/question/<int:question_id>/', vote_views.vote_question, name='vote_question'),
    path('vote/answer/<int:answer_id>/', vote_views.vote_answer, name='vote_answer'),

    # static file insecure setting
    url(r'^static/(?P<path>.*)', serve, kwargs={'insecure': True})
]