from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.User)
admin.site.register(models.Condition)
admin.site.register(models.RiskScore)
admin.site.register(models.Population)
admin.site.register(models.Activity)
admin.site.register(models.ActivityStatus)
admin.site.register(models.ActivityAnswer)
admin.site.register(models.Signature)
admin.site.register(models.ConsentPDF)

