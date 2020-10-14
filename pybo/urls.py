from django.urls import path

from .views import base_views, question_views, editor_views, answer_views, comment_views, vote_views

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
    path('editor/subtitle', editor_views.editor_subtitle, name='editor_subtitle'),
    path('editor/keyword', editor_views.editor_keyword, name='editor_keyword'),
    path('editor/keyword/save', editor_views.editor_keyword_save, name='editor_keyword_save'),
    path('editor/keyword/search', editor_views.editor_keyword_search, name='editor_keyword_search'),
    path('editor/keyword/selectdown', editor_views.editor_keyword_select_download, name='editor_keyword_select_download'),

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
]
