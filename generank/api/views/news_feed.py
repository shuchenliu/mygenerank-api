from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication

from oauth2_provider.ext.rest_framework.authentication import OAuth2Authentication

from ..models import Item
from ..permissions import IsActive
from ..serializers import ItemSerializer


class ItemViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """ A newsfeed that allows the user to keep up to date on recent news
    in the medical field.

    list:
    Get the user's newsfeed.
    """
    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [IsAuthenticated, IsActive]
    queryset = Item.objects.all().order_by('-created_on')
    serializer_class = ItemSerializer
