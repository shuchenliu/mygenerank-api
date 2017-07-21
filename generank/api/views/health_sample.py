from rest_framework import viewsets, mixins
from rest_framework import filters as django_filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from oauth2_provider.ext.rest_framework.authentication import OAuth2Authentication

from .. import filters
from ..models import HealthSample
from ..serializers import HealthSampleSerializer


class HealthSampleViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """ API endpoint that allows health samples to be viewed or edited. """
    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = HealthSample.objects.all().order_by('-end_date')
    serializer_class = HealthSampleSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)
    search_fields = ['user__id', 'identifier', 'start_date', 'end_date']

    def create(self, request, *args, **kwargs):
        """ Override allows for bulk upload due to heavy volume of requests.
        source: http://stackoverflow.com/questions/37329771/django-rest-bulk-post-post-array-of-json-objects#37332640
        """
        try:
            data = request.data['objects']
        except KeyError:
            data = request.data

        is_many = True if isinstance(data, list) else False
        serializer = self.get_serializer(data=data, many=is_many)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    def get(self, request, *args, **kwargs):
        """ A simple API that returns the date of the last health sample that
        has been uploaded for the given user.
        """
        queryset = self.filter_queryset(self.get_queryset())
        if len(queryset) == 0:
            return Response(None, status=404)
        last = queryset[0]
        return Response({
            'end_date': last.end_date.strftime('%Y-%m-%dT%H:%M:%S'),
            'identifier': last.identifier.value
        }, status=200)
