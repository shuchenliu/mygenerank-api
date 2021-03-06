from django.core.exceptions import ObjectDoesNotExist
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response

from ..models import Population, User, RiskScore, Activity, \
    Condition, ActivityAnswer, ActivityStatus, Signature, \
    ConsentPDF, HealthSample, HealthSampleIdentifier

class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'url': {'view_name': 'user-detail'}
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
            view_name='consentpdf-detail',
            many=False,
            queryset=ConsentPDF.objects.all()
        )

    class Meta:
        model = Signature
        fields = ('url', 'date_signed', 'consent_pdf', 'consent_signed')

    def validate_consent_pdf(self, value):
        user = self.context['request'].user
        if value not in user.consent_pdfs.all():
            raise serializers.ValidationError('Invalid value for consent form.')
        return value


class ConsentPDFSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(
            view_name='user-detail',
            many=False,
            read_only=True
        )

    class Meta:
        model = ConsentPDF
        fields = ('url', 'consent_pdf', 'user', 'name')
        extra_kwargs = {
            'signature': {'read_only': True},
            'url': {'view_name': 'consentpdf-detail'}
        }

    def create(self, validated_data):
        return ConsentPDF.objects.create(
            **validated_data, user=self.context['request'].user)
