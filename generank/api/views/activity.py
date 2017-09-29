from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, mixins
from rest_framework import filters as django_filters
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, authentication_classes

from oauth2_provider.ext.rest_framework.authentication import OAuth2Authentication

from .. import filters
from ..models import User, Activity, ActivityStatus, ActivityAnswer
from ..permissions import IsActive
from ..serializers import ActivityAnswerSerializer, ActivitySerializer, \
    ActivityStatusSerializer


class ActivityViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """ Activities are a task that the user must complete during the study.
    These could be things like asnwering surveys or authorizing data use.

    Activities have no user ownership. For a list of the activities that a
    given user must complete or has completed, see ActivityStatus.

    list:
    This endpoint will list all of the activites currently available
    during the study.

    retrieve:
    Fetch a single instance of a given activity by {id}.
    """
    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [IsAuthenticated, IsActive]
    queryset = Activity.objects.all().order_by('-name')
    serializer_class = ActivitySerializer


class ActivityAnswerViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """ Every activity has 1 or more answers associated with it based on the
    number and type of questions asked.

    list:
    Retrieve a list of all of the answers to questions the user has answered.

    retrieve:
    Fetch a given answer by its {id}.

    create:
    Add a new answer to a question in a given activity. The activity question
    identifier can be any identifier to a given question. Identifiers are not
    enforced, using one from the list of utilized identifiers is encouraged.
    """
    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [IsAuthenticated, IsActive]
    queryset = ActivityAnswer.objects.all().order_by('-user')
    serializer_class = ActivityAnswerSerializer
    search_fields = ['user__id','question_identifier']
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)


class ActivityStatusViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """ Activity Answers contain the information about an activity regarding a
    given user and whether or not the user has completed the activity.

    list:
    This endpoint will list all of the statuses that the user has or should
    complete. If a status for an activity is not present, then the user should
    not complete this activity.

    retrieve:
    Fetch a single instance of a given status by {id}.

    update:
    Once a given activity is complete a user's status for that activity should
    be updated to reflect the completion.
    """
    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [IsAuthenticated, IsActive]
    queryset = ActivityStatus.objects.all().order_by('-user')
    serializer_class = ActivityStatusSerializer
    filter_backends = (filters.IsOwnerFilterBackend, django_filters.SearchFilter)
    search_fields = ['user__id', 'activity__id', 'activity__name', 'question_identifier']

