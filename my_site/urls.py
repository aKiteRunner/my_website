from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^index$', index, name='index'),
    url(r'^user/register$', register, name='register'),
    url(r'^user/login$', user_login, name='login'),
    url(r'^user/logout$', user_logout, name='logout'),
    url(r'^user/(?P<user_id>[0-9]+)/index$', show_user_profile, name='show_user_profile'),
    url(r'^user/edit$', edit_user_profile, name='edit_user_profile'),
    url(r'^user/password$', edit_user_password, name='edit_user_password'),
    url(r'^user/authority$', edit_user_authority, name='edit_user_authority'),

    url(r'^category/index$', show_categories, name='categories'),
    url(r'^category/add$', add_category, name='add_category'),
    url(r'^category/(?P<category_id>[0-9]+)/index$', show_category, name='category_detail'),
    url(r'^category/(?P<category_id>[0-9]+)/update$', update_category, name='update_category'),
    url(r'^category/(?P<category_id>[0-9]+)/rank$', show_category_rank, name='category_rank'),

    url(r'^question/index$', show_questions, name='questions'),
    url(r'^question/add$', add_question, name='add_question'),
    url(r'^question/(?P<question_id>[0-9]+)/index$', show_question, name='question_detail'),
    url(r'^question/(?P<question_id>[0-9]+)/submit$', answer_submit, name='submit'),
    url(r'^question/(?P<question_id>[0-9]+)/submission$', show_question_submissions, name='submission'),
    url(r'^question/(?P<question_id>[0-9]+)/update$', update_question, name='update_question'),

    url(r'^submission/index$', show_submissions, name='submissions'),
    url(r'^submission/(?P<submission_id>[0-9]+)/index', show_submission, name='show_submission'),
    url(r'^submission/(?P<submission_id>[0-9]+)/edit', edit_submission, name='edit_submission'),

    url(r'^exam/index$', show_exams, name='exams'),
    url(r'^exam/(?P<exam_id>[0-9]+)/index', show_exam, name='exam_detail'),
    url(r'^exam/(?P<exam_id>[0-9]+)/question/(?P<question_id>[0-9]+)/index',
        show_exam_question, name='exam_question_detail'),
    url(r'^exam/(?P<exam_id>[0-9]+)/question/(?P<question_id>[0-9]+)/submit',
        exam_answer_submit, name='exam_submit'),
    url(r'^exam/(?P<exam_id>[0-9]+)/question/(?P<question_id>[0-9]+)/submission',
        show_exam_question_submissions, name='exam_submission'),
    url(r'^exam/add$', add_exam, name='add_exam'),
    url(r'^exam/(?P<exam_id>[0-9]+)/update$', update_exam, name='update_exam'),
    url(r'exam/(?P<exam_id>[0-9]+)/rank$', show_exam_rank, name='exam_rank'),
    url(r'exam/generate$', generate_random_exam, name='generate_exam'),

    url(r'^test$', test, name='test')
]
