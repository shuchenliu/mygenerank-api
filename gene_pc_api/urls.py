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
from rest_framework.authtoken import views
from rest_framework import routers

from push_notifications.api.rest_framework import APNSDeviceAuthorizedViewSet, \
    GCMDeviceAuthorizedViewSet

from gene_pc_api.gene_pc_api import views as gpc_views
from gene_pc_api.twentythreeandme import views as ttm_views
from rest_framework.authtoken import views
from rest_framework import routers


api_router = routers.DefaultRouter()
api_router.register(r'users', gpc_views.UserViewSet)
api_router.register(r'activities', gpc_views.ActivityViewSet)
api_router.register(r'conditions', gpc_views.ConditionViewSet)
api_router.register(r'populations', gpc_views.PopulationViewSet)
api_router.register(r'activity-answers', gpc_views.ActivityAnswerViewSet)
api_router.register(r'activity-statuses', gpc_views.ActivityStatusViewSet)
api_router.register(r'risk-scores', gpc_views.RiskScoreViewSet)

api_router.register(r'device/apns', APNSDeviceAuthorizedViewSet)
api_router.register(r'device/gcm', GCMDeviceAuthorizedViewSet)


ttm_router = routers.DefaultRouter()
ttm_router.register(r'users', ttm_views.UserViewSet)
ttm_router.register(r'profiles', ttm_views.ProfileViewSet)
ttm_router.register(r'genomes', ttm_views.GenotypeViewSet)


urlpatterns = [
    # Public API
    url(r'^api/', include(
            api_router.urls,
            namespace="api",
            app_name='gene_pc_api'
        )
    ),
    url(r'^api/o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^api/register/', gpc_views.CreateUserView.as_view()),
    url(r'^api/import23andme/', gpc_views.import23andme),

    # Internal API
    url(r'^twentythreeandme/', include(ttm_router.urls,
        namespace="twentythreeandme", app_name='twentythreeandme')),

    # Admin
    url(r'^admin/', admin.site.urls),
]
