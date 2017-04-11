from django.core.exceptions import ObjectDoesNotExist
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response

from ..models import Population, User, RiskScore, Condition


class PopulationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Population
        fields = ('url', 'name',)
        extra_kwargs = {'url': {'view_name': 'api:population-detail'}}


class ConditionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Condition
        fields = ('url', 'name', 'overview', 'description',
        'risk_explanation', 'multiple_scores_explanation',
        'supporting_evidence', 'follow_up_activity_identifier')
        extra_kwargs = {'url': {'view_name': 'api:condition-detail'}}


class RiskScoreSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
            view_name='api:user-detail',
            many=False,
            queryset=User.objects.all()
        )
    condition = serializers.HyperlinkedRelatedField(
            view_name='api:condition-detail',
            many=False,
            queryset=Condition.objects.all()
        )

    population = serializers.HyperlinkedRelatedField(
            view_name='api:population-detail',
            many=False,
            queryset=Population.objects.all()
        )

    class Meta:
        model = RiskScore
        fields = ('url', 'user', 'name', 'value', 'description',
            'condition', 'population', 'calculated', 'featured')
        extra_kwargs = {'url': {'view_name': 'api:riskscore-detail'}}
