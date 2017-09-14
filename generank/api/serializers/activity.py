from django.core.exceptions import ObjectDoesNotExist
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response

from ..models import Activity, ActivityAnswer, ActivityStatus, User


class ActivitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Activity
        fields = ('url', 'name', 'subtitle', 'study_task_identifier', 'type')


class ActivityStatusSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
            view_name='user-detail',
            many=False,
            queryset=User.objects.all()
        )
    activity = serializers.HyperlinkedRelatedField(
            view_name='activity-detail',
            many=False,
            queryset=Activity.objects.all()
        )

    class Meta:
        model = ActivityStatus
        fields = ('url', 'user', 'activity', 'complete')


class ActivityAnswerSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
            view_name='user-detail',
            many=False,
            read_only=True
        )
    activity = serializers.HyperlinkedRelatedField(
            view_name='activity-detail',
            many=False,
            queryset=Activity.objects.all()
        )

    class Meta:
        model = ActivityAnswer
        fields = ('url', 'user', 'question_identifier', 'value', 'activity')

    def create(self, validated_data):
        user = self.context['request'].user
        return ActivityAnswer.objects.create(**validated_data, user=user)


