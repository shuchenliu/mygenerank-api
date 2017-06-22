from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer

from generank.api import models
from . import newsfeed


@api_view(['GET'])
@renderer_classes((TemplateHTMLRenderer,))
def home_view(request):
    users_count = models.User.objects.all().count()
    return Response({
        'title': 'MyGeneRank | Unlock your genetic risk',
        'users': users_count
    }, template_name='home.html')


@api_view(['GET'])
@renderer_classes((TemplateHTMLRenderer,))
def team_view(request):
    return Response({
        'title': 'MyGeneRank | The Team'
    }, template_name='team.html')


@api_view(['GET'])
@renderer_classes((TemplateHTMLRenderer,))
def contact_view(request):
    return Response({
        'title': 'MyGeneRank | Contact Us'
    }, template_name='contact.html')
