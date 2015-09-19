from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^questionnaire/$', 'questionnaire.views.welcome'),
                       url(r'^questionnaire/(?P<question_id>\d+)/$', 'questionnaire.views.detail'),
                       url(r'^questionnaire/(?P<question_id>\d+)/vote/$', 'questionnaire.views.vote'),
                       url(r'^questionnaire/completed/$', 'questionnaire.views.completed'),
                       url(r'^questionnaire/logout/$', 'questionnaire.views.logout'),
                       url(r'^questionnaire/logout/save/$', 'knapsack.views.savePayout'),
                       url(r'^knapsack/$', 'knapsack.views.start'),
                       url(r'^knapsack/(?P<round_nr>\d+)/$', 'knapsack.views.index'),
                       url(r'^knapsack/(?P<round_nr>\d+)/save/$', 'knapsack.views.save'),
                       url(r'^knapsack/(?P<round_nr>\d+)/full/$', 'knapsack.views.full'),
                       url(r'^welcome/(?P<welcome_nr>\d+)/$', 'knapsack.views.welcome'),
                       url(r'^welcome/$', 'knapsack.views.start'),
                       url(r'^data/$', 'knapsack.views.statistics'),
                       url(r'^data/export_round/$', 'knapsack.views.export_round'),
                       url(r'^data/export_box/$', 'knapsack.views.export_box'),
                       url(r'^data/export_stat/$', 'knapsack.views.export_stat'),
                       url(r'^data/export_user/$', 'knapsack.views.export_user'),
                       url(r'^data/export_payout/$', 'knapsack.views.export_payout'),
                       url(r'^data/export_answer/$', 'questionnaire.views.export_answer'),
                       url(r'^data/export_feedback/$', 'questionnaire.views.export_feedback'),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^accounts/login/$',  login),
                       url(r'^accounts/logout/$', logout,{'next_page': 'logged_out'}, name='auth_logout'),
                       url(r'^test/(?P<user_group>\d+)/$', 'knapsack.views.test'),
                       )