""" GeneRank URL Configuration """
from django.contrib import admin
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

from rest_framework.authtoken import views
from rest_framework import routers, schemas, renderers
from rest_framework_swagger.views import get_swagger_view

from push_notifications.api.rest_framework import APNSDeviceAuthorizedViewSet, \
    GCMDeviceAuthorizedViewSet

from . import views
from . import signals


api_router = routers.DefaultRouter()
api_router.register(r'users', views.UserViewSet)
api_router.register(r'activities', views.ActivityViewSet)
api_router.register(r'conditions', views.ConditionViewSet)
api_router.register(r'populations', views.PopulationViewSet)
api_router.register(r'activity-answers', views.ActivityAnswerViewSet)
api_router.register(r'activity-statuses', views.ActivityStatusViewSet)
api_router.register(r'risk-scores', views.RiskScoreViewSet)
api_router.register(r'signatures', views.SignatureViewSet)
api_router.register(r'consent-forms', views.ConsentPDFViewSet)
api_router.register(r'health-samples', views.HealthSampleViewSet)
api_router.register(r'lifestyle', views.LifestyleMetricStatusViewSet)
api_router.register(r'newsfeed', views.ItemViewSet)

private_api_router = routers.DefaultRouter()
private_api_router.register(r'device/apns', APNSDeviceAuthorizedViewSet)
private_api_router.register(r'device/gcm', GCMDeviceAuthorizedViewSet)


public_api = [
    url(r'^api/', include(
            api_router.urls,
        )
    ),
    url(r'^api/o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]

schema_view = schema_view = get_swagger_view(
    title='MyGeneRank Public API',
    #description='This document described the public interface to MyGeneRank. Except \
#where otherwise noted, an authenticated user account is required to access all endpoints.',
    patterns=public_api,
    urlconf='api.urls',
)

urlpatterns = [
    url(r'^api/register/', views.CreateUserView.as_view()),
    url(r'^api/schema/', schema_view),

    url(r'^api/', include(
            private_api_router.urls,
        )
    ),
] + public_api
