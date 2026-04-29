from django.urls import path
from .views import (
    EmergencyPatientListCreateView,
    EmergencyPatientDetailView,
    ConvertEmergencyPatientView,
)

urlpatterns = [
    path('', EmergencyPatientListCreateView.as_view(), name='emergency-list-create'),
    path('<int:pk>/', EmergencyPatientDetailView.as_view(), name='emergency-detail'),
    path('<int:pk>/convert/', ConvertEmergencyPatientView.as_view(), name='emergency-convert'),
]
