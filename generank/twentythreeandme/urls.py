""" GeneRank URL Configuration """
from django.contrib import admin
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views

from rest_framework.authtoken import views
from rest_framework import routers

from . import views

ttm_router = routers.DefaultRouter()
ttm_router.register(r'users', views.UserViewSet)
ttm_router.register(r'profiles', views.ProfileViewSet)
ttm_router.register(r'genotypes', views.GenotypeViewSet)
ttm_router.register(r'settings', views.SettingsViewSet)


urlpatterns = [
    url(r'^twentythreeandme/', include(
            ttm_router.urls,
            namespace='ttm_router',
            app_name='ttm_router'
        )
    ),
    url(r'^twentythreeandme/import/', views.import_data),
]
