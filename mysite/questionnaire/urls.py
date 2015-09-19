from django.conf.urls.defaults import *

from questionnaire import views

urlpatterns = patterns('',
                       url(r'^$', views.index, name='index')
                       )