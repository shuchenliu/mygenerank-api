from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response

from generank.compute.tasks import cad

from ..models import (Population, User, RiskScore, Condition,
    RiskReductor, RiskReductorOption)


class RiskReductorOptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RiskReductorOption
        fields = ('value', 'name', 'identifier')


class RiskReductorSerializer(serializers.HyperlinkedModelSerializer):
    options = serializers.SerializerMethodField()
    active = serializers.SerializerMethodField()

    class Meta:
        model = RiskReductor
        fields = ('name', 'identifier', 'options', 'active', 'description')

    def get_options(self, reductor):
        if reductor.options.count() > 0:
            serializer = RiskReductorOptionSerializer(reductor.options, many=True)
            return serializer.data

    def get_active(self, reductor):
        user = getattr(self.context['request'], 'user', None)
        if user:
            return self.active_status_for_user(reductor, user)

    def active_status_for_user(self, reductor, user):
        """ Returns a given user's active status based on how they answered
        their survey questions. We assume that this method will not be called
        unless the user actually has a valid status for the given reductor.

        Note:
        Responses are noted by {identifier}_default for all default responses.
        """
        responses = cad.get_survey_responses(user.id)
        return responses.get(reductor.identifier+'_default', False)


class PopulationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Population
        fields = ('url', 'name',)


class ConditionSerializer(serializers.HyperlinkedModelSerializer):
    reductors = serializers.SerializerMethodField()

    class Meta:
        model = Condition
        fields = ('url', 'name', 'overview', 'description',
        'risk_explanation', 'multiple_scores_explanation', 'is_modifiable_by_behavior',
        'supporting_evidence', 'follow_up_activity_identifier', 'reductors')

    def get_reductors(self, condition):
        # Before showing any risk reductors, make sure that the user has
        # filled in the required information for them.
        try:
            user = getattr(self.context['request'], 'user', None)
            cad.get_survey_responses(user.id)
        except ObjectDoesNotExist, MultipleObjectsReturned:
            return None
        serializer = RiskReductorSerializer(condition.reductors,
            many=True, context=self.context)
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
    predict = serializers.HyperlinkedIdentityField(
        view_name='riskscore-predict'
    )

    class Meta:
        model = RiskScore
        fields = ('url', 'user', 'name', 'value', 'description',
            'condition', 'population', 'calculated', 'featured', 'predict')
