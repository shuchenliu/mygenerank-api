"""gene_pc_api URL Configuration """
from django.contrib import admin
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.authtoken import views
from rest_framework import routers

from push_notifications.api.rest_framework import APNSDeviceAuthorizedViewSet, \
    GCMDeviceAuthorizedViewSet

from gene_pc_api.gene_pc_api import views as gpc_views
from gene_pc_api.twentythreeandme import views as ttm_views
from gene_pc_api.gene_pc_api import signals


api_router = routers.DefaultRouter()
api_router.register(r'users', gpc_views.UserViewSet)
api_router.register(r'activities', gpc_views.ActivityViewSet)
api_router.register(r'conditions', gpc_views.ConditionViewSet)
api_router.register(r'populations', gpc_views.PopulationViewSet)
api_router.register(r'activity-answers', gpc_views.ActivityAnswerViewSet)
api_router.register(r'activity-statuses', gpc_views.ActivityStatusViewSet)
api_router.register(r'risk-scores', gpc_views.RiskScoreViewSet)
api_router.register(r'signatures', gpc_views.SignatureViewSet)
api_router.register(r'consent-forms', gpc_views.ConsentPDFViewSet)

api_router.register(r'device/apns', APNSDeviceAuthorizedViewSet)
api_router.register(r'device/gcm', GCMDeviceAuthorizedViewSet)


ttm_router = routers.DefaultRouter()
ttm_router.register(r'users', ttm_views.UserViewSet)
ttm_router.register(r'profiles', ttm_views.ProfileViewSet)
ttm_router.register(r'genomes', ttm_views.GenotypeViewSet)


urlpatterns = ([
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
] + static(settings.CONSENT_FILE_URL, document_root=settings.CONSENT_FILE_LOCATION)
    + static(settings.TTM_RAW_URL, document_root=settings.TTM_RAW_STORAGE)
    + static(settings.TTM_CONVERTED_URL, document_root=settings.TTM_CONVERTED_STORAGE)
    + static(settings.DATA_URL, document_root=settings.DATA_STORAGE)
)
