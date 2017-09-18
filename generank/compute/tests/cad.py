import os, unittest, uuid
from unittest import mock

from django.test import TestCase
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from generank import api
from generank.twentythreeandme import models
from .. import tasks


class MockUser():
    id = uuid.uuid4()


MODULE_PATH = os.path.dirname(__file__)
GENOTYPE_FIXTURE_PATH = os.path.abspath(os.path.join(os.path.dirname(MODULE_PATH), 'fixtures', 'genotypes'))


class TestCADTasks(TestCase):

    def setUp(self):
        # Set up activities
        for study_id in settings.DEFAULT_STUDY_IDS:
            api.models.Activity.objects.create(study_task_identifier=study_id)

        self.api_user = api.models.User.objects.create(username='test@test')
        self.user = models.User.objects.create(api_user_id=self.api_user.id)
        self.profile = models.Profile.objects.create(user=self.user, profile_id='test', genotyped=True)
        self.genotype = models.Genotype.objects.create(profile=self.profile)

    def check_responses(self, user_id, data, answers):
        def mock_get_answer(identifier, user):
            try:
                return data[identifier]
            except KeyError:
                raise ObjectDoesNotExist('identifier')

        with mock.patch('generank.compute.tasks.cad._get_answer', side_effect=mock_get_answer):
            with mock.patch('generank.compute.tasks.cad._get_bool_answer', side_effect=mock_get_answer):
                with mock.patch('generank.compute.tasks.cad._get_value_answer', side_effect=mock_get_answer):
                    with mock.patch('generank.api.models.User.objects.get', return_value=MockUser()):
                        responses = tasks.cad.get_survey_responses(user_id)
                        for key, value in responses.items():
                            self.assertEqual(value, answers[key])


    def test_healthy_white_male_53(self):
        self.check_responses(uuid.uuid4(), {
            settings.SEX_QUESTION_IDENTIFIER: 'male',
            settings.RACIAL_QUESTION_IDENTIFIER: 'white',
            settings.HEIGHT_QUESTION_IDENTIFIER: 75,
            settings.WEIGHT_QUESTION_IDENTIFIER: 170,
            settings.AGE_QUESTION_IDENTIFIER: 53,
            settings.TOTAL_CHOLESTEROL_IDENTIFIER: 130,
            settings.PRECISE_TOTAL_CHOLESTEROL_IDENTIFIER: 200,
            settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 110,
            settings.PRECISE_HDL_CHOLESTEROL_IDENTIFIER: 80,
            settings.BLOOD_PRESSURE_QUESTION_IDENTIFIER: '',
            settings.SYSTOLIC_BLOOD_PRESSURE_IDENTIFIER: 120,
            settings.DIABETES_IDENTIFIER: False,
            settings.SMOKING_IDENTIFIER: False,
            settings.ACTIVITY_IDENTIFIER: True,
            settings.DIET_IDENTIFIER: True,
            settings.BLOOD_PRESSURE_MEDICATION_IDENTIFIER: True,
            # Deprecated
#             settings.ANCESTRY_QUESTION_IDENTIFIER: '',
        }, {
            "sex": 'male',
            "ancestry": False,
            "age": 53,
            "diabetic": False,
            "HDL_cholesterol": 80,
            "total_cholesterol": 200,
            "systolicBP_untreated": 1,
            "systolicBP_treated": 120.0,
            "non_smoking_default": True,
            "healthy_weight_default": True,
            "physical_activity_default": True,
            "healthy_diet_default": True,
            "average_odds": 1.32
        })

    def test_healthy_black_male_33(self):
        self.check_responses(uuid.uuid4(), {
            settings.SEX_QUESTION_IDENTIFIER: 'male',
            settings.RACIAL_QUESTION_IDENTIFIER: 'african_american',
            settings.HEIGHT_QUESTION_IDENTIFIER: 75,
            settings.WEIGHT_QUESTION_IDENTIFIER: 170,
            settings.AGE_QUESTION_IDENTIFIER: 33,
            settings.TOTAL_CHOLESTEROL_IDENTIFIER: 130,
            settings.PRECISE_TOTAL_CHOLESTEROL_IDENTIFIER: 200,
            settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 110,
            settings.PRECISE_HDL_CHOLESTEROL_IDENTIFIER: 80,
            settings.BLOOD_PRESSURE_QUESTION_IDENTIFIER: '',
            settings.SYSTOLIC_BLOOD_PRESSURE_IDENTIFIER: 120,
            settings.DIABETES_IDENTIFIER: False,
            settings.SMOKING_IDENTIFIER: False,
            settings.ACTIVITY_IDENTIFIER: True,
            settings.DIET_IDENTIFIER: True,
            settings.BLOOD_PRESSURE_MEDICATION_IDENTIFIER: True,
            # Deprecated
#             settings.ANCESTRY_QUESTION_IDENTIFIER: '',
        }, {
            "sex": 'male',
            "ancestry": True,
            "age": 49,
            "diabetic": False,
            "HDL_cholesterol": 80,
            "total_cholesterol": 200,
            "systolicBP_untreated": 1,
            "systolicBP_treated": 120.0,
            "non_smoking_default": True,
            "healthy_weight_default": True,
            "physical_activity_default": True,
            "healthy_diet_default": True,
            "average_odds": 1.32
        })


    def test_unhealthy_black_male_80(self):
        self.check_responses(uuid.uuid4(), {
            settings.SEX_QUESTION_IDENTIFIER: 'male',
            settings.RACIAL_QUESTION_IDENTIFIER: 'african_american',
            settings.HEIGHT_QUESTION_IDENTIFIER: 75,
            settings.WEIGHT_QUESTION_IDENTIFIER: 270,
            settings.AGE_QUESTION_IDENTIFIER: 80,
            settings.TOTAL_CHOLESTEROL_IDENTIFIER: 130,
            settings.PRECISE_TOTAL_CHOLESTEROL_IDENTIFIER: 200,
            settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 110,
            settings.PRECISE_HDL_CHOLESTEROL_IDENTIFIER: 80,
            settings.BLOOD_PRESSURE_QUESTION_IDENTIFIER: '',
            settings.SYSTOLIC_BLOOD_PRESSURE_IDENTIFIER: 120,
            settings.DIABETES_IDENTIFIER: True,
            settings.SMOKING_IDENTIFIER: True,
            settings.ACTIVITY_IDENTIFIER: False,
            settings.DIET_IDENTIFIER: False,
            settings.BLOOD_PRESSURE_MEDICATION_IDENTIFIER: True,
            # Deprecated
#             settings.ANCESTRY_QUESTION_IDENTIFIER: '',
        }, {
            "sex": 'male',
            "ancestry": True,
            "age": 79,
            "diabetic": True,
            "HDL_cholesterol": 80,
            "total_cholesterol": 200,
            "systolicBP_untreated": 1,
            "systolicBP_treated": 120.0,
            "non_smoking_default": False,
            "healthy_weight_default": False,
            "physical_activity_default": False,
            "healthy_diet_default": False,
            "average_odds": 1.32
        })

    def test_deprecated_unhealthy_black_male_80(self):
        self.check_responses(uuid.uuid4(), {
            settings.SEX_QUESTION_IDENTIFIER: 'male',
#             settings.RACIAL_QUESTION_IDENTIFIER: 'african_american',
            settings.HEIGHT_QUESTION_IDENTIFIER: 75,
            settings.WEIGHT_QUESTION_IDENTIFIER: 270,
            settings.AGE_QUESTION_IDENTIFIER: 80,
            settings.TOTAL_CHOLESTEROL_IDENTIFIER: 130,
            settings.PRECISE_TOTAL_CHOLESTEROL_IDENTIFIER: 200,
            settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 110,
            settings.PRECISE_HDL_CHOLESTEROL_IDENTIFIER: 80,
            settings.BLOOD_PRESSURE_QUESTION_IDENTIFIER: '',
            settings.SYSTOLIC_BLOOD_PRESSURE_IDENTIFIER: 120,
            settings.DIABETES_IDENTIFIER: True,
            settings.SMOKING_IDENTIFIER: True,
            settings.ACTIVITY_IDENTIFIER: False,
            settings.DIET_IDENTIFIER: False,
            settings.BLOOD_PRESSURE_MEDICATION_IDENTIFIER: True,
            # Deprecated
            settings.ANCESTRY_QUESTION_IDENTIFIER: True,
        }, {
            "sex": 'male',
            "ancestry": True,
            "age": 79,
            "diabetic": True,
            "HDL_cholesterol": 80,
            "total_cholesterol": 200,
            "systolicBP_untreated": 1,
            "systolicBP_treated": 120.0,
            "non_smoking_default": False,
            "healthy_weight_default": False,
            "physical_activity_default": False,
            "healthy_diet_default": False,
            "average_odds": 1.32
        })

    def test_deprecated_unhealthy_white_female_80(self):
        self.check_responses(uuid.uuid4(), {
            settings.SEX_QUESTION_IDENTIFIER: 'female',
#             settings.RACIAL_QUESTION_IDENTIFIER: 'african_american',
            settings.HEIGHT_QUESTION_IDENTIFIER: 75,
            settings.WEIGHT_QUESTION_IDENTIFIER: 270,
            settings.AGE_QUESTION_IDENTIFIER: 80,
            settings.TOTAL_CHOLESTEROL_IDENTIFIER: 130,
            settings.PRECISE_TOTAL_CHOLESTEROL_IDENTIFIER: 200,
            settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 110,
            settings.PRECISE_HDL_CHOLESTEROL_IDENTIFIER: 80,
            settings.BLOOD_PRESSURE_QUESTION_IDENTIFIER: '',
            settings.SYSTOLIC_BLOOD_PRESSURE_IDENTIFIER: 120,
            settings.DIABETES_IDENTIFIER: True,
            settings.SMOKING_IDENTIFIER: True,
            settings.ACTIVITY_IDENTIFIER: False,
            settings.DIET_IDENTIFIER: False,
            settings.BLOOD_PRESSURE_MEDICATION_IDENTIFIER: True,
            # Deprecated
            settings.ANCESTRY_QUESTION_IDENTIFIER: False,
        }, {
            "sex": 'female',
            "ancestry": False,
            "age": 79,
            "diabetic": True,
            "HDL_cholesterol": 80,
            "total_cholesterol": 200,
            "systolicBP_untreated": 1,
            "systolicBP_treated": 120.0,
            "non_smoking_default": False,
            "healthy_weight_default": False,
            "physical_activity_default": False,
            "healthy_diet_default": False,
            "average_odds": 1.32
        })


    def test_no_blood_pressure_meds(self):
        self.check_responses(uuid.uuid4(), {
            settings.SEX_QUESTION_IDENTIFIER: 'male',
            settings.RACIAL_QUESTION_IDENTIFIER: 'african_american',
            settings.HEIGHT_QUESTION_IDENTIFIER: 75,
            settings.WEIGHT_QUESTION_IDENTIFIER: 270,
            settings.AGE_QUESTION_IDENTIFIER: 80,
            settings.TOTAL_CHOLESTEROL_IDENTIFIER: 130,
            settings.PRECISE_TOTAL_CHOLESTEROL_IDENTIFIER: 200,
            settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 110,
            settings.PRECISE_HDL_CHOLESTEROL_IDENTIFIER: 80,
            settings.BLOOD_PRESSURE_QUESTION_IDENTIFIER: '',
            settings.SYSTOLIC_BLOOD_PRESSURE_IDENTIFIER: 120,
            settings.DIABETES_IDENTIFIER: True,
            settings.SMOKING_IDENTIFIER: True,
            settings.ACTIVITY_IDENTIFIER: False,
            settings.DIET_IDENTIFIER: False,
            settings.BLOOD_PRESSURE_MEDICATION_IDENTIFIER: False,
        }, {
            "sex": 'male',
            "ancestry": True,
            "age": 79,
            "diabetic": True,
            "HDL_cholesterol": 80,
            "total_cholesterol": 200,
            "systolicBP_untreated": 120.0,
            "systolicBP_treated": 1,
            "non_smoking_default": False,
            "healthy_weight_default": False,
            "physical_activity_default": False,
            "healthy_diet_default": False,
            "average_odds": 1.32
        })

    def test_moderate_blood_pressure(self):
        self.check_responses(uuid.uuid4(), {
            settings.SEX_QUESTION_IDENTIFIER: 'female',
            settings.RACIAL_QUESTION_IDENTIFIER: 'african_american',
            settings.HEIGHT_QUESTION_IDENTIFIER: 75,
            settings.WEIGHT_QUESTION_IDENTIFIER: 270,
            settings.AGE_QUESTION_IDENTIFIER: 80,
            settings.TOTAL_CHOLESTEROL_IDENTIFIER: 130,
            settings.PRECISE_TOTAL_CHOLESTEROL_IDENTIFIER: 200,
            settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 110,
            settings.PRECISE_HDL_CHOLESTEROL_IDENTIFIER: 80,
            settings.BLOOD_PRESSURE_QUESTION_IDENTIFIER: 'moderate',
#             settings.SYSTOLIC_BLOOD_PRESSURE_IDENTIFIER: 120,
            settings.DIABETES_IDENTIFIER: True,
            settings.SMOKING_IDENTIFIER: True,
            settings.ACTIVITY_IDENTIFIER: False,
            settings.DIET_IDENTIFIER: False,
            settings.BLOOD_PRESSURE_MEDICATION_IDENTIFIER: True,
        }, {
            "sex": 'female',
            "ancestry": True,
            "age": 79,
            "diabetic": True,
            "HDL_cholesterol": 80,
            "total_cholesterol": 200,
            "systolicBP_untreated": 1,
            "systolicBP_treated": 145,
            "non_smoking_default": False,
            "healthy_weight_default": False,
            "physical_activity_default": False,
            "healthy_diet_default": False,
            "average_odds": 1.32
        })


    def test_high_blood_pressure(self):
        self.check_responses(uuid.uuid4(), {
            settings.SEX_QUESTION_IDENTIFIER: 'female',
            settings.RACIAL_QUESTION_IDENTIFIER: 'african_american',
            settings.HEIGHT_QUESTION_IDENTIFIER: 75,
            settings.WEIGHT_QUESTION_IDENTIFIER: 270,
            settings.AGE_QUESTION_IDENTIFIER: 80,
            settings.TOTAL_CHOLESTEROL_IDENTIFIER: 130,
            settings.PRECISE_TOTAL_CHOLESTEROL_IDENTIFIER: 200,
            settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 110,
            settings.PRECISE_HDL_CHOLESTEROL_IDENTIFIER: 80,
            settings.BLOOD_PRESSURE_QUESTION_IDENTIFIER: 'high',
            settings.DIABETES_IDENTIFIER: True,
            settings.SMOKING_IDENTIFIER: True,
            settings.ACTIVITY_IDENTIFIER: False,
            settings.DIET_IDENTIFIER: False,
            settings.BLOOD_PRESSURE_MEDICATION_IDENTIFIER: True,
        }, {
            "sex": 'female',
            "ancestry": True,
            "age": 79,
            "diabetic": True,
            "HDL_cholesterol": 80,
            "total_cholesterol": 200,
            "systolicBP_untreated": 1,
            "systolicBP_treated": 170,
            "non_smoking_default": False,
            "healthy_weight_default": False,
            "physical_activity_default": False,
            "healthy_diet_default": False,
            "average_odds": 1.32
        })

    def test_low_blood_pressure(self):
        self.check_responses(uuid.uuid4(), {
            settings.SEX_QUESTION_IDENTIFIER: 'female',
            settings.RACIAL_QUESTION_IDENTIFIER: 'african_american',
            settings.HEIGHT_QUESTION_IDENTIFIER: 75,
            settings.WEIGHT_QUESTION_IDENTIFIER: 270,
            settings.AGE_QUESTION_IDENTIFIER: 80,
            settings.TOTAL_CHOLESTEROL_IDENTIFIER: 130,
            settings.PRECISE_TOTAL_CHOLESTEROL_IDENTIFIER: 200,
            settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 110,
            settings.PRECISE_HDL_CHOLESTEROL_IDENTIFIER: 80,
            settings.BLOOD_PRESSURE_QUESTION_IDENTIFIER: 'low',
            settings.DIABETES_IDENTIFIER: True,
            settings.SMOKING_IDENTIFIER: True,
            settings.ACTIVITY_IDENTIFIER: False,
            settings.DIET_IDENTIFIER: False,
            settings.BLOOD_PRESSURE_MEDICATION_IDENTIFIER: True,
        }, {
            "sex": 'female',
            "ancestry": True,
            "age": 79,
            "diabetic": True,
            "HDL_cholesterol": 80,
            "total_cholesterol": 200,
            "systolicBP_untreated": 1,
            "systolicBP_treated": 110,
            "non_smoking_default": False,
            "healthy_weight_default": False,
            "physical_activity_default": False,
            "healthy_diet_default": False,
            "average_odds": 1.32
        })

    def test_low_cholesterol(self):
        self.check_responses(uuid.uuid4(), {
            settings.SEX_QUESTION_IDENTIFIER: 'female',
            settings.RACIAL_QUESTION_IDENTIFIER: 'african_american',
            settings.HEIGHT_QUESTION_IDENTIFIER: 75,
            settings.WEIGHT_QUESTION_IDENTIFIER: 270,
            settings.AGE_QUESTION_IDENTIFIER: 80,
            settings.TOTAL_CHOLESTEROL_IDENTIFIER: 130,
            settings.PRECISE_TOTAL_CHOLESTEROL_IDENTIFIER: 200,
            settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 'low',
            settings.BLOOD_PRESSURE_QUESTION_IDENTIFIER: 'low',
            settings.DIABETES_IDENTIFIER: True,
            settings.SMOKING_IDENTIFIER: True,
            settings.ACTIVITY_IDENTIFIER: False,
            settings.DIET_IDENTIFIER: False,
            settings.BLOOD_PRESSURE_MEDICATION_IDENTIFIER: True,
        }, {
            "sex": 'female',
            "ancestry": True,
            "age": 79,
            "diabetic": True,
            "HDL_cholesterol": 35,
            "total_cholesterol": 200,
            "systolicBP_untreated": 1,
            "systolicBP_treated": 110,
            "non_smoking_default": False,
            "healthy_weight_default": False,
            "physical_activity_default": False,
            "healthy_diet_default": False,
            "average_odds": 1.32
        })

    def test_moderate_cholesterol(self):
        self.check_responses(uuid.uuid4(), {
            settings.SEX_QUESTION_IDENTIFIER: 'female',
            settings.RACIAL_QUESTION_IDENTIFIER: 'african_american',
            settings.HEIGHT_QUESTION_IDENTIFIER: 75,
            settings.WEIGHT_QUESTION_IDENTIFIER: 270,
            settings.AGE_QUESTION_IDENTIFIER: 80,
            settings.TOTAL_CHOLESTEROL_IDENTIFIER: 130,
            settings.PRECISE_TOTAL_CHOLESTEROL_IDENTIFIER: 200,
            settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 'moderate',
            settings.BLOOD_PRESSURE_QUESTION_IDENTIFIER: 'low',
            settings.DIABETES_IDENTIFIER: True,
            settings.SMOKING_IDENTIFIER: True,
            settings.ACTIVITY_IDENTIFIER: False,
            settings.DIET_IDENTIFIER: False,
            settings.BLOOD_PRESSURE_MEDICATION_IDENTIFIER: True,
        }, {
            "sex": 'female',
            "ancestry": True,
            "age": 79,
            "diabetic": True,
            "HDL_cholesterol": 50,
            "total_cholesterol": 200,
            "systolicBP_untreated": 1,
            "systolicBP_treated": 110,
            "non_smoking_default": False,
            "healthy_weight_default": False,
            "physical_activity_default": False,
            "healthy_diet_default": False,
            "average_odds": 1.32
        })

    def test_high_cholesterol(self):
        self.check_responses(uuid.uuid4(), {
            settings.SEX_QUESTION_IDENTIFIER: 'female',
            settings.RACIAL_QUESTION_IDENTIFIER: 'african_american',
            settings.HEIGHT_QUESTION_IDENTIFIER: 75,
            settings.WEIGHT_QUESTION_IDENTIFIER: 270,
            settings.AGE_QUESTION_IDENTIFIER: 80,
            settings.TOTAL_CHOLESTEROL_IDENTIFIER: 130,
            settings.PRECISE_TOTAL_CHOLESTEROL_IDENTIFIER: 200,
            settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 'high',
            settings.BLOOD_PRESSURE_QUESTION_IDENTIFIER: 'low',
            settings.DIABETES_IDENTIFIER: True,
            settings.SMOKING_IDENTIFIER: True,
            settings.ACTIVITY_IDENTIFIER: False,
            settings.DIET_IDENTIFIER: False,
            settings.BLOOD_PRESSURE_MEDICATION_IDENTIFIER: True,
        }, {
            "sex": 'female',
            "ancestry": True,
            "age": 79,
            "diabetic": True,
            "HDL_cholesterol": 65,
            "total_cholesterol": 200,
            "systolicBP_untreated": 1,
            "systolicBP_treated": 110,
            "non_smoking_default": False,
            "healthy_weight_default": False,
            "physical_activity_default": False,
            "healthy_diet_default": False,
            "average_odds": 1.32
        })

    def test_high_total_cholesterol(self):
        self.check_responses(uuid.uuid4(), {
            settings.SEX_QUESTION_IDENTIFIER: 'female',
            settings.RACIAL_QUESTION_IDENTIFIER: 'african_american',
            settings.HEIGHT_QUESTION_IDENTIFIER: 75,
            settings.WEIGHT_QUESTION_IDENTIFIER: 270,
            settings.AGE_QUESTION_IDENTIFIER: 80,
            settings.TOTAL_CHOLESTEROL_IDENTIFIER: 'high',
            settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 'high',
            settings.BLOOD_PRESSURE_QUESTION_IDENTIFIER: 'low',
            settings.DIABETES_IDENTIFIER: True,
            settings.SMOKING_IDENTIFIER: True,
            settings.ACTIVITY_IDENTIFIER: False,
            settings.DIET_IDENTIFIER: False,
            settings.BLOOD_PRESSURE_MEDICATION_IDENTIFIER: True,
        }, {
            "sex": 'female',
            "ancestry": True,
            "age": 79,
            "diabetic": True,
            "HDL_cholesterol": 65,
            "total_cholesterol": 250,
            "systolicBP_untreated": 1,
            "systolicBP_treated": 110,
            "non_smoking_default": False,
            "healthy_weight_default": False,
            "physical_activity_default": False,
            "healthy_diet_default": False,
            "average_odds": 1.32
        })

    def test_moderate_total_cholesterol(self):
        self.check_responses(uuid.uuid4(), {
            settings.SEX_QUESTION_IDENTIFIER: 'female',
            settings.RACIAL_QUESTION_IDENTIFIER: 'african_american',
            settings.HEIGHT_QUESTION_IDENTIFIER: 75,
            settings.WEIGHT_QUESTION_IDENTIFIER: 270,
            settings.AGE_QUESTION_IDENTIFIER: 80,
            settings.TOTAL_CHOLESTEROL_IDENTIFIER: 'moderate',
            settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 'high',
            settings.BLOOD_PRESSURE_QUESTION_IDENTIFIER: 'low',
            settings.DIABETES_IDENTIFIER: True,
            settings.SMOKING_IDENTIFIER: True,
            settings.ACTIVITY_IDENTIFIER: False,
            settings.DIET_IDENTIFIER: False,
            settings.BLOOD_PRESSURE_MEDICATION_IDENTIFIER: True,
        }, {
            "sex": 'female',
            "ancestry": True,
            "age": 79,
            "diabetic": True,
            "HDL_cholesterol": 65,
            "total_cholesterol": 220,
            "systolicBP_untreated": 1,
            "systolicBP_treated": 110,
            "non_smoking_default": False,
            "healthy_weight_default": False,
            "physical_activity_default": False,
            "healthy_diet_default": False,
            "average_odds": 1.32
        })

    def test_low_total_cholesterol(self):
        self.check_responses(uuid.uuid4(), {
            settings.SEX_QUESTION_IDENTIFIER: 'female',
            settings.RACIAL_QUESTION_IDENTIFIER: 'african_american',
            settings.HEIGHT_QUESTION_IDENTIFIER: 75,
            settings.WEIGHT_QUESTION_IDENTIFIER: 270,
            settings.AGE_QUESTION_IDENTIFIER: 80,
            settings.TOTAL_CHOLESTEROL_IDENTIFIER: 'low',
            settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 'high',
            settings.BLOOD_PRESSURE_QUESTION_IDENTIFIER: 'low',
            settings.DIABETES_IDENTIFIER: True,
            settings.SMOKING_IDENTIFIER: True,
            settings.ACTIVITY_IDENTIFIER: False,
            settings.DIET_IDENTIFIER: False,
            settings.BLOOD_PRESSURE_MEDICATION_IDENTIFIER: True,
        }, {
            "sex": 'female',
            "ancestry": True,
            "age": 79,
            "diabetic": True,
            "HDL_cholesterol": 65,
            "total_cholesterol": 190,
            "systolicBP_untreated": 1,
            "systolicBP_treated": 110,
            "non_smoking_default": False,
            "healthy_weight_default": False,
            "physical_activity_default": False,
            "healthy_diet_default": False,
            "average_odds": 1.32
        })

    # Missing Data Tests

    def test_invalid_sex(self):
        def wrapper():
            self.check_responses(uuid.uuid4(), {
                settings.SEX_QUESTION_IDENTIFIER: '--female--',
            }, {})
        self.assertRaises(ValueError, wrapper)

    def test_missing_sex(self):
        def wrapper():
            self.check_responses(uuid.uuid4(), {}, {})
        self.assertRaises(ObjectDoesNotExist, wrapper)

    def test_missing_ancestry(self):
        def wrapper():
            self.check_responses(uuid.uuid4(), {
                settings.SEX_QUESTION_IDENTIFIER: 'female',
            }, {})
        self.assertRaises(ObjectDoesNotExist, wrapper)

    def test_missing_age(self):
        def wrapper():
            self.check_responses(uuid.uuid4(), {
                settings.SEX_QUESTION_IDENTIFIER: 'female',
                settings.ANCESTRY_QUESTION_IDENTIFIER: False,
            }, {})
        self.assertRaises(ObjectDoesNotExist, wrapper)

    def test_missing_diabetes(self):
        def wrapper():
            self.check_responses(uuid.uuid4(), {
                settings.SEX_QUESTION_IDENTIFIER: 'female',
                settings.ANCESTRY_QUESTION_IDENTIFIER: False,
                settings.AGE_QUESTION_IDENTIFIER: 80,
            }, {})
        self.assertRaises(ObjectDoesNotExist, wrapper)

    def test_missing_hdl_cholesterol(self):
        def wrapper():
            self.check_responses(uuid.uuid4(), {
                settings.SEX_QUESTION_IDENTIFIER: 'female',
                settings.ANCESTRY_QUESTION_IDENTIFIER: False,
                settings.AGE_QUESTION_IDENTIFIER: 80,
                settings.DIABETES_IDENTIFIER: True,
           }, {})
        self.assertRaises(ObjectDoesNotExist, wrapper)

    def test_missing_total_cholesterol(self):
        def wrapper():
            self.check_responses(uuid.uuid4(), {
                settings.SEX_QUESTION_IDENTIFIER: 'female',
                settings.ANCESTRY_QUESTION_IDENTIFIER: False,
                settings.AGE_QUESTION_IDENTIFIER: 80,
                settings.DIABETES_IDENTIFIER: True,
                settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 110,
           }, {})
        self.assertRaises(ObjectDoesNotExist, wrapper)

    def test_missing_systolic_blood_pressure(self):
        def wrapper():
            self.check_responses(uuid.uuid4(), {
                settings.SEX_QUESTION_IDENTIFIER: 'female',
                settings.ANCESTRY_QUESTION_IDENTIFIER: False,
                settings.AGE_QUESTION_IDENTIFIER: 80,
                settings.DIABETES_IDENTIFIER: True,
                settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 110,
                settings.TOTAL_CHOLESTEROL_IDENTIFIER: 130,
           }, {})
        self.assertRaises(ObjectDoesNotExist, wrapper)

    def test_missing_smoking(self):
        def wrapper():
            self.check_responses(uuid.uuid4(), {
                settings.SEX_QUESTION_IDENTIFIER: 'female',
                settings.ANCESTRY_QUESTION_IDENTIFIER: False,
                settings.AGE_QUESTION_IDENTIFIER: 80,
                settings.DIABETES_IDENTIFIER: True,
                settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 110,
                settings.TOTAL_CHOLESTEROL_IDENTIFIER: 130,
                settings.SYSTOLIC_BLOOD_PRESSURE_IDENTIFIER: 120,
           }, {})
        self.assertRaises(ObjectDoesNotExist, wrapper)

    def test_missing_healthy_weight(self):
        def wrapper():
            self.check_responses(uuid.uuid4(), {
                settings.SEX_QUESTION_IDENTIFIER: 'female',
                settings.ANCESTRY_QUESTION_IDENTIFIER: False,
                settings.AGE_QUESTION_IDENTIFIER: 80,
                settings.DIABETES_IDENTIFIER: True,
                settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 110,
                settings.TOTAL_CHOLESTEROL_IDENTIFIER: 130,
                settings.SYSTOLIC_BLOOD_PRESSURE_IDENTIFIER: 120,
                settings.SMOKING_IDENTIFIER: True,
           }, {})
        self.assertRaises(ObjectDoesNotExist, wrapper)

    def test_missing_activity(self):
        def wrapper():
            self.check_responses(uuid.uuid4(), {
                settings.SEX_QUESTION_IDENTIFIER: 'female',
                settings.ANCESTRY_QUESTION_IDENTIFIER: False,
                settings.AGE_QUESTION_IDENTIFIER: 80,
                settings.DIABETES_IDENTIFIER: True,
                settings.TOTAL_HDL_CHOLESTEROL_IDENTIFIER: 110,
                settings.TOTAL_CHOLESTEROL_IDENTIFIER: 130,
                settings.SYSTOLIC_BLOOD_PRESSURE_IDENTIFIER: 120,
                settings.SMOKING_IDENTIFIER: True,
                settings.HEIGHT_QUESTION_IDENTIFIER: 75,
                settings.WEIGHT_QUESTION_IDENTIFIER: 270,
           }, {})
        self.assertRaises(ObjectDoesNotExist, wrapper)

    # Test Steps

    def test_get_ancestry(self):
        with open(os.sep.join((GENOTYPE_FIXTURE_PATH, 'test_genotype.vcf'))) as fp:
            self.genotype.converted_file = mock.MagicMock(return_value=fp)
            r = tasks.cad.get_ancestry(self.api_user.id.hex)
        self.assertEqual(r, ('some id 1', 'some/ancestry/path', '0.01 0.02 0.03 0.03 0.3\n'))

    def test_get_cad_haplotypes(self):
        with open(os.sep.join((GENOTYPE_FIXTURE_PATH, 'test_genotype.vcf'))) as fp:
            self.genotype.converted_file = mock.MagicMock(return_value=fp)
            r = tasks.cad._get_cad_haplotypes(self.api_user.id.hex, '4')
        self.assertEqual(r, ('some_id_2', 'some/file/path', 'some data from the file'))

    def test_impute_and_get_cad_risk_per_chunk(self):
        with open(os.sep.join((GENOTYPE_FIXTURE_PATH, 'test_genotype.vcf'))) as fp:
            self.genotype.converted_file = mock.MagicMock(return_value=fp)
            r = tasks.cad._impute_and_get_cad_risk_per_chunk(
                ('some_id_2', 'some/file/path', 'some data from the file'),
                self.api_user.id.hex,
                (1, 1, 0, 1)
            )
        self.assertEqual(r, ('some_id_3', 'some/file/path', 'some data from the file'))

    def test_get_total_cad_risk(self):
        with open(os.sep.join((GENOTYPE_FIXTURE_PATH, 'test_genotype.vcf'))) as fp:
            self.genotype.converted_file = mock.MagicMock(return_value=fp)
            r = tasks.cad._get_total_cad_risk(
                (
                    ('some_id_3', 'some/file/ancestry/path', 'ancestry data'),
                    ('some_id_3', 'some/file/path', 'some data from the file'),
                    ('some_id_3', 'some/file/path', 'some data from the file'),
                ),
                self.api_user.id.hex,
            )
        self.assertEqual(
            r,
            ('ancestry data', '/path/to/score', '0.0001\n0.02\n0.1\n0.0003\n0.32\n0.78')
        )
