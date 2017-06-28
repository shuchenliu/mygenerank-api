from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication

from oauth2_provider.ext.rest_framework.authentication import OAuth2Authentication

from ..models import Item
from ..serializers import ItemSerializer


class ItemViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """ API endpoint that allows activities to be viewed or edited. """
    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Item.objects.all().order_by('-created_on')
    serializer_class = ItemSerializer
