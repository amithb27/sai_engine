from django.contrib import admin
from .models import *
from django.apps import apps
# Register your models here.

def registerModels():
    models = apps.get_models()
    sailytics_modles = [model for model in models if model._meta.app_config.name == 'sailytics']
    for model in sailytics_modles:
        admin.site.register(model)

registerModels()


