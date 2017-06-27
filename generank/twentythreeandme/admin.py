from django.contrib import admin

from . import models

# Register your models here.
admin.site.register(models.User)
admin.site.register(models.APIToken)
admin.site.register(models.Profile)
admin.site.register(models.Genotype)
admin.site.register(models.Settings)