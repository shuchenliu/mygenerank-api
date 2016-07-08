from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response

from .models import Population, User, RiskScore, Activity, \
    Condition, ActivityAnswer, ActivityStatus, Signature, ConsentPDF

class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'url': {'view_name': 'api:user-detail'}
        }

    def create(self, validated_data):
            user = User(
                email=validated_data['username'],
                username=validated_data['username']
            )
            user.set_password(validated_data['password'])
            user.save()
            return user

class SignatureSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
            view_name='api:user-detail',
            many=False,
            queryset=User.objects.all()
        )

    class Meta:
        model = Signature
        fields = ('url', 'date_signed', 'user', 'consent_signed')
        extra_kwargs = {'url': {'view_name': 'api:consentpdf-detail'}}


class ConsentPDFSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
            view_name='api:user-detail',
            many=False,
            queryset=User.objects.all()
        )

    class Meta:
        model = ConsentPDF
        fields = ('url', 'consent_pdf', 'user')
        extra_kwargs = {'url': {'view_name': 'api:consentpdf-detail'}}



class PopulationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Population
        fields = ('url', 'name',)
        extra_kwargs = {'url': {'view_name': 'api:population-detail'}}


class ConditionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Condition
        fields = ('url', 'name', 'overview', 'description')
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


class ActivitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Activity
        fields = ('url', 'name', 'subtitle', 'study_task_identifier')
        extra_kwargs = {'url': {'view_name': 'api:activity-detail'}}


class ActivityStatusSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
            view_name='api:user-detail',
            many=False,
            queryset=User.objects.all()
        )
    activity = serializers.HyperlinkedRelatedField(
            view_name='api:activity-detail',
            many=False,
            queryset=Activity.objects.all()
        )

    class Meta:
        model = ActivityStatus
        fields = ('url', 'user', 'activity', 'complete')
        extra_kwargs = {'url': {'view_name': 'api:activitystatus-detail'}}


class ActivityAnswerSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
            view_name='api:user-detail',
            many=False,
            queryset=User.objects.all()
        )
    activity = serializers.HyperlinkedRelatedField(
            view_name='api:activity-detail',
            many=False,
            queryset=Activity.objects.all()
        )

    class Meta:
        model = ActivityAnswer
        fields = ('url', 'user', 'question_identifier', 'value', 'activity')
        extra_kwargs = {'url': {'view_name': 'api:activityanswer-detail'}}



