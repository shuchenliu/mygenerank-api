from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from oauth2_provider.ext.rest_framework.authentication import OAuth2Authentication

from ..models import Item
from ..serializers import ItemSerializer


class ItemViewSet(viewsets.ModelViewSet):
    """ API endpoint that allows activities to be viewed or edited. """
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]
    queryset = Item.objects.all().order_by('-created_on')
    serializer_class = ItemSerializer
