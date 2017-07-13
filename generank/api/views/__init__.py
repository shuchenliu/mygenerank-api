from rest_framework import routers, schemas, renderers
from rest_framework_swagger import renderers as swagger_renderers
from rest_framework.decorators import api_view, renderer_classes

from .activity import ActivityViewSet, ActivityStatusViewSet, ActivityAnswerViewSet
from .condition import ConditionViewSet, PopulationViewSet, RiskScoreViewSet
from .health_sample import HealthSampleViewSet
from .lifestyle import LifestyleMetricStatusViewSet
from .news_feed import ItemViewSet
from .user import UserViewSet, CreateUserView, ConsentPDFViewSet, SignatureViewSet
