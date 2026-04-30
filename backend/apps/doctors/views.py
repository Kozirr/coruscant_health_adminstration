from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import DoctorProfile, Prescription
from .serializers import DoctorProfileSerializer, PrescriptionSerializer


class DoctorProfileListCreateView(generics.ListCreateAPIView):
    serializer_class = DoctorProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return DoctorProfile.objects.all()
        if user.role == 'DOCTOR':
            return DoctorProfile.objects.filter(user=user)
        return DoctorProfile.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role != 'DOCTOR':
            raise PermissionDenied('Only doctors can create doctor profiles.')
        if DoctorProfile.objects.filter(user=self.request.user).exists():
            raise PermissionDenied('Doctor profile already exists.')
        serializer.save(user=self.request.user)


class DoctorProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DoctorProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return DoctorProfile.objects.all()
        if user.role == 'DOCTOR':
            return DoctorProfile.objects.filter(user=user)
        return DoctorProfile.objects.none()


class PrescriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.role in ('ADMIN', 'DOCTOR'):
            qs = Prescription.objects.all()
        elif user.role == 'PATIENT':
            qs = Prescription.objects.filter(patient__user=user)
        else:
            qs = Prescription.objects.none()
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            qs = qs.filter(patient_id=patient_id)
        return qs

    def perform_create(self, serializer):
        if self.request.user.role != 'DOCTOR':
            raise PermissionDenied('Only doctors can create prescriptions.')
        doctor = get_object_or_404(DoctorProfile, user=self.request.user)
        serializer.save(doctor=doctor)


class PrescriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.role in ('ADMIN', 'DOCTOR'):
            return Prescription.objects.all()
        if user.role == 'PATIENT':
            return Prescription.objects.filter(patient__user=user)
        return Prescription.objects.none()

    def perform_update(self, serializer):
        if self.request.user.role != 'DOCTOR':
            raise PermissionDenied('Only doctors can update prescriptions.')
        if serializer.instance.doctor.user != self.request.user:
            raise PermissionDenied('Doctors can only update prescriptions they created.')
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.role != 'DOCTOR':
            raise PermissionDenied('Only doctors can delete prescriptions.')
        if instance.doctor.user != self.request.user:
            raise PermissionDenied('Doctors can only delete prescriptions they created.')
        instance.delete()
