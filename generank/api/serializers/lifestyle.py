from django.core.exceptions import ObjectDoesNotExist
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response

from ..models import LifestyleMetric, LifestyleMetricStatus, Condition, \
    LifestyleMetricScore, LifestyleMetricGoal, LifestyleMetricSeries, User


class LifestyleMetricScoreSerializer(serializers.HyperlinkedModelSerializer):
    created_on = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", required=False)

    class Meta:
        model = LifestyleMetricScore
        fields = ('value', 'created_on')


class LifestyleMetricGoalSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LifestyleMetricGoal
        fields = ('value', 'name')


class LifestyleMetricSeriesSerializer(serializers.HyperlinkedModelSerializer):
    conditions = serializers.HyperlinkedRelatedField(
            view_name='api:condition-detail',
            many=True,
            queryset=Condition.objects.all()
        )
    values = serializers.SerializerMethodField()
    personal_best = serializers.SerializerMethodField()
    goals = LifestyleMetricGoalSerializer(many=True)

    class Meta:
        model = LifestyleMetricSeries
        fields = ('values', 'name', 'conditions', 'personal_best', 'goals')


    def get_personal_best(self, series):
        try:
            personal_best = LifestyleMetricScore.objects.get(series=series, is_personal_best=True)
        except ObjectDoesNotExist:
            return None

        serializer = LifestyleMetricScoreSerializer(instance=personal_best)
        return serializer.data

    def get_values(self, series):
        scores = LifestyleMetricScore.objects.filter(series=series).order_by('-created_on')[:10]
        serializer = LifestyleMetricScoreSerializer(scores, many=True)
        return serializer.data


class LifestyleMetricSerializer(serializers.HyperlinkedModelSerializer):
    series = LifestyleMetricSeriesSerializer(many=True)

    class Meta:
        model = LifestyleMetric
        fields = ('identifier', 'name', 'series')


class LifestyleMetricStatusSerializer(serializers.HyperlinkedModelSerializer):
    metric = LifestyleMetricSerializer()
    last_updated = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", required=False)

    class Meta:
        model = LifestyleMetricStatus
        fields = ('url', 'metric', 'last_updated')
        extra_kwargs = {'url': {'view_name': 'api:lifestylemetricstatus-detail'}}
