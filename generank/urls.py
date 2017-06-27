""" GeneRank URL Configuration """
from django.contrib import admin
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views


urlpatterns = ([
    url('^', include('django.contrib.auth.urls')),
    url('^', include('generank.website.urls')),
    url('^', include('generank.api.urls')),
    url('^', include('generank.twentythreeandme.urls')),

    # Admin
    url(r'^admin/', admin.site.urls),

] + static(settings.CONSENT_FILE_URL, document_root=settings.CONSENT_FILE_LOCATION)
    + static(settings.TTM_RAW_URL, document_root=settings.TTM_RAW_STORAGE)
    + static(settings.TTM_CONVERTED_URL, document_root=settings.TTM_CONVERTED_STORAGE)
    + static(settings.DATA_URL, document_root=settings.DATA_STORAGE)
)
