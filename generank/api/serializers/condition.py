from django.core.exceptions import ObjectDoesNotExist
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response

from ..models import (Population, User, RiskScore, Condition,
    RiskReductor, RiskReductorOption)


class RiskReductorOptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RiskReductorOption
        fields = ('value', 'name', 'identifier')


class RiskReductorSerializer(serializers.HyperlinkedModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = RiskReductor
        fields = ('value', 'name', 'identifier', 'options')

    def get_options(self, reductor):
        if reductor.options.count() > 0:
            serializer = RiskReductorOptionSerializer(reductor.options, many=True)
            return serializer.data
        return None


class PopulationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Population
        fields = ('url', 'name',)


class ConditionSerializer(serializers.HyperlinkedModelSerializer):
    reductors = serializers.SerializerMethodField()

    class Meta:
        model = Condition
        fields = ('url', 'name', 'overview', 'description',
        'risk_explanation', 'multiple_scores_explanation',
        'supporting_evidence', 'follow_up_activity_identifier', 'reductors')

    def get_reductors(self, condition):
        serializer = RiskReductorSerializer(condition.reductors, many=True)
        return serializer.data


class RiskScoreSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
            view_name='user-detail',
            many=False,
            queryset=User.objects.all()
        )
    condition = serializers.HyperlinkedRelatedField(
            view_name='condition-detail',
            many=False,
            queryset=Condition.objects.all()
        )

    population = serializers.HyperlinkedRelatedField(
            view_name='population-detail',
            many=False,
            queryset=Population.objects.all()
        )

    class Meta:
        model = RiskScore
        fields = ('url', 'user', 'name', 'value', 'description',
            'condition', 'population', 'calculated', 'featured')
