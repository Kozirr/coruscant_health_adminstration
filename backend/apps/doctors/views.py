from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404

from apps.core.permissions import IsAdmin, IsAdminOrDoctor
from .models import DoctorProfile, Prescription
from .serializers import DoctorProfileSerializer, PrescriptionSerializer


class DoctorProfileListCreateView(generics.ListCreateAPIView):
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DoctorProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)


class PrescriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = (IsAdminOrDoctor,)

    def get_queryset(self):
        qs = Prescription.objects.all()
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            qs = qs.filter(patient_id=patient_id)
        return qs

    def perform_create(self, serializer):
        doctor = get_object_or_404(DoctorProfile, user=self.request.user)
        serializer.save(doctor=doctor)


class PrescriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)
