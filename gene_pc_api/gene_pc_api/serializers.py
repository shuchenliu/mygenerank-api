from rest_framework import serializers

from .models import Phenotypes, User, RiskScores

class UserSerializer(serializers.HyperlinkedModelSerializer):
    phenotypes = serializers.HyperlinkedRelatedField(
            view_name='api:phenotypes-detail',
            many=False,
            read_only=True
        )

    risk_scores = serializers.HyperlinkedRelatedField(
            view_name='api:riskscores-detail',
            many=False,
            read_only=True
        )

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'phenotypes', 'risk_scores',
            'profile_id', 'auth_code')
        write_only_fields = ('auth_code',)
        extra_kwargs = {'url': {'view_name': 'api:user-detail'}}


class PhenotypesSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
            view_name='api:user-detail',
            many=False,
            queryset=User.objects.all()
        )

    class Meta:
        model = Phenotypes
        fields = ('url', 'user', 'age', 'sex', 'smoking_status',
            'total_cholesterol', 'hdl_cholesterol', 'systolic_blood_pressure',
            'taking_blood_pressure_medication')
        extra_kwargs = {'url': {'view_name': 'api:phenotypes-detail'}}


class RiskScoresSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
            view_name='api:user-detail',
            many=False,
            queryset=User.objects.all()
        )

    class Meta:
        model = RiskScores
        fields = ('url', 'user', 'framingham_score')
        extra_kwargs = {'url': {'view_name': 'api:riskscores-detail'}}
