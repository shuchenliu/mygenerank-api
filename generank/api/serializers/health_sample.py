from django.core.exceptions import ObjectDoesNotExist
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response

from ..models import User, HealthSample, HealthSampleIdentifier


class HealthSampleIdentifierSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HealthSampleIdentifier
        fields = ('value',)


class HealthSampleSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
            view_name='user-detail',
            many=False,
            queryset=User.objects.all()
        )
    identifier = HealthSampleIdentifierSerializer()
    start_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", required=False)
    end_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", required=False)
    collected_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", required=False)

    class Meta:
        model = HealthSample
        fields = ('url', 'user', 'identifier', 'value', 'units', 'end_date', 'start_date', 'collected_date')
        extra_kwargs = {'url': {'view_name': 'healthsample-detail'}}

    def create(self, validated_data):
        try:
            identifier = HealthSampleIdentifier.object.get(value=validated_data['identifier'])
        except ObjectDoesNotExist:
            identifier = HealthSampleIdentifier(value=validated_data['identifier'])
            validated_data['identifier'] = identifier.id
            identifier.save()

        return HealthSample.object.create(**validated_data)


