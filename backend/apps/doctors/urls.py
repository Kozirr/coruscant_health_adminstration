from django.urls import path
from .views import (
    DoctorProfileListCreateView,
    DoctorProfileDetailView,
    PrescriptionListCreateView,
    PrescriptionDetailView,
)

urlpatterns = [
    path('', DoctorProfileListCreateView.as_view(), name='doctor-list-create'),
    path('<int:pk>/', DoctorProfileDetailView.as_view(), name='doctor-detail'),
    path('prescriptions/', PrescriptionListCreateView.as_view(), name='prescription-list-create'),
    path('prescriptions/<int:pk>/', PrescriptionDetailView.as_view(), name='prescription-detail'),
]
