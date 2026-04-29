from django.contrib import admin
from .models import DoctorProfile, Prescription

admin.site.register(DoctorProfile)
admin.site.register(Prescription)
