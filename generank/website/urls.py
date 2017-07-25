""" GeneRank URL Configuration """
from django.conf.urls import url, include

from . import views


urlpatterns = [
#     Accounts/Registration
    url(r'^accounts/',
        include('rest_framework.urls', namespace='rest_framework')),

    url(r'^$', views.home_view),
    url(r'^team/$', views.team_view),
    url(r'^contact/$', views.contact_view),
    url(r'^privacy/$', views.privacy_policy_view),
    url(r'^news/$', views.newsfeed.NewsFeedView.as_view()),
]
