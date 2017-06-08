import logging, uuid

from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer

from .activity import ActivityViewSet, ActivityStatusViewSet, ActivityAnswerViewSet
from .condition import ConditionViewSet, PopulationViewSet, RiskScoreViewSet
from .health_sample import HealthSampleViewSet
from .lifestyle import LifestyleMetricStatusViewSet
from .news_feed import ItemViewSet
from .user import UserViewSet, CreateUserView, ConsentPDFViewSet, SignatureViewSet


@api_view(['GET'])
@renderer_classes((TemplateHTMLRenderer,))
def about_page(request):
    return Response({}, template_name='about.html')
