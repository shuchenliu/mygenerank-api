from django.contrib import admin

from . import models


# Register your models here.
admin.site.register(models.User)
admin.site.register(models.Condition)
admin.site.register(models.RiskScore)
admin.site.register(models.Population)
admin.site.register(models.RiskReductor)
admin.site.register(models.RiskReductorOption)
admin.site.register(models.Activity)
admin.site.register(models.ActivityStatus)
admin.site.register(models.ActivityAnswer)
admin.site.register(models.Signature)
admin.site.register(models.ConsentPDF)
admin.site.register(models.HealthSample)
admin.site.register(models.HealthSampleIdentifier)
admin.site.register(models.Ancestry)
admin.site.register(models.LifestyleMetric)
admin.site.register(models.LifestyleMetricSeries)
admin.site.register(models.LifestyleMetricScore)
admin.site.register(models.LifestyleMetricStatus)
admin.site.register(models.LifestyleMetricGoal)
admin.site.register(models.Item)
