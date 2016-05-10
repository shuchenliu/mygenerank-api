"""gene_pc_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from rest_framework import routers
from gene_pc_api.gene_pc_api import views as gpc_views
from gene_pc_api.twentythreeandme import views as ttm_views


api_router = routers.DefaultRouter()
api_router.register(r'users', gpc_views.UserViewSet)
api_router.register(r'phenotypes', gpc_views.PhenotypesViewSet)
api_router.register(r'risk-scores', gpc_views.RiskScoresViewSet)
api_router.register(r'activities', gpc_views.ActivitiesViewSet)


ttm_router = routers.DefaultRouter()
ttm_router.register(r'users', ttm_views.UserViewSet)
ttm_router.register(r'profiles', ttm_views.ProfileViewSet)
ttm_router.register(r'genomes', ttm_views.GenomeViewSet)


urlpatterns = [
    url(r'^api/', include(api_router.urls, namespace="api",
        app_name='gene_pc_api')),
    url(r'^twentythreeandme/', include(ttm_router.urls,
        namespace="twentythreeandme", app_name='twentythreeandme')),
    #url(r'^admin/', admin.site.urls),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
        url(r'^import23andme/', gpc_views.import23andme)
]
