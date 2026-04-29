from django.contrib import admin
from .models import PatientProfile, HealthReading

admin.site.register(PatientProfile)
admin.site.register(HealthReading)
