from django.contrib import admin
from .models import YieldPrediction, DiseasePrediction

admin.site.register(YieldPrediction)
admin.site.register(DiseasePrediction)