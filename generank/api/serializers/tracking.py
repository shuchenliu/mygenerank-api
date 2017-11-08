from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework import status
from rest_framework.compat import is_authenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse

from ..models import User, TrackedEvent


class TrackedEventSerializer(serializers.ModelSerializer):
    user = serializers.HyperlinkedRelatedField(
            view_name='user-detail',
            many=False,
            read_only=True
        )
    name = serializers.CharField()
    view = serializers.CharField()
    created_on = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", required=False)

    class Meta:
        model = TrackedEvent
        fields = ('user', 'name', 'view', 'created_on')

    def validate_created_on(self, created_on_int):
        try:
            created_on = datetime.utcfromtimestamp()
        except Exception:
            raise serializers.ValidationError("Invalid creation date.")
        return created_on

    def create(self, validated_data):
        context_user = self.context['request'].user
        user = context_user if is_authenticated(context_user) else None
        return TrackedEvent.objects.create(**validated_data, user=user)
