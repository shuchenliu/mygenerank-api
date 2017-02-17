from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response

from .models import Population, User, RiskScore, Activity, \
    Condition, ActivityAnswer, ActivityStatus, Signature, \
    ConsentPDF, HealthSample

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
    consent_pdf = serializers.HyperlinkedRelatedField(
            view_name='api:consentpdf-detail',
            many=False,
            queryset=ConsentPDF.objects.all()
        )

    class Meta:
        model = Signature
        fields = ('url', 'date_signed', 'consent_pdf', 'consent_signed')
        extra_kwargs = {'url': {'view_name': 'api:signatures-detail'}}


class ConsentPDFSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
            view_name='api:user-detail',
            many=False,
            queryset=User.objects.all()
        )

    class Meta:
        model = ConsentPDF
        fields = ('url', 'consent_pdf', 'user', 'name')
        extra_kwargs = {
            'signature': {'read_only': True},
            'url': {'view_name': 'api:consentpdf-detail'}
        }


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


class ActivitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Activity
        fields = ('url', 'name', 'subtitle', 'study_task_identifier', 'type')
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


class HealthSampleSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
            view_name='api:user-detail',
            many=False,
            queryset=User.objects.all()
        )
    start_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", required=False)
    end_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", required=False)

    class Meta:
        model = HealthSample
        fields = ('url', 'user', 'identifier', 'value', 'units', 'end_date', 'start_date')
        extra_kwargs = {'url': {'view_name': 'api:healthsample-detail'}}



