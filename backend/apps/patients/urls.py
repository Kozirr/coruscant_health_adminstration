from django.urls import path
from .views import (
    PatientProfileListCreateView,
    PatientProfileDetailView,
    HealthReadingListCreateView,
    HealthReadingUploadView,
)

urlpatterns = [
    path('', PatientProfileListCreateView.as_view(), name='patient-list-create'),
    path('<int:pk>/', PatientProfileDetailView.as_view(), name='patient-detail'),
    path('<int:patient_id>/readings/', HealthReadingListCreateView.as_view(), name='reading-list-create'),
    path('<int:patient_id>/readings/upload/', HealthReadingUploadView.as_view(), name='reading-upload'),
]
