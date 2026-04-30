import csv
import io
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import PatientProfile, HealthReading
from .serializers import PatientProfileSerializer, HealthReadingSerializer


class PatientProfileListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.role in ('ADMIN', 'DOCTOR'):
            return PatientProfile.objects.all()
        if user.role == 'PATIENT':
            return PatientProfile.objects.filter(user=user)
        return PatientProfile.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role != 'PATIENT':
            raise PermissionDenied('Only patients can create their own patient profile.')
        if PatientProfile.objects.filter(user=self.request.user).exists():
            raise PermissionDenied('Patient profile already exists.')
        serializer.save(user=self.request.user)


class PatientProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.role in ('ADMIN', 'DOCTOR'):
            return PatientProfile.objects.all()
        if user.role == 'PATIENT':
            return PatientProfile.objects.filter(user=user)
        return PatientProfile.objects.none()

    def perform_update(self, serializer):
        if self.request.user.role not in ('ADMIN', 'PATIENT'):
            raise PermissionDenied('Only administrators and profile owners can update patient profiles.')
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.role != 'ADMIN':
            raise PermissionDenied('Only administrators can delete patient profiles.')
        instance.delete()


class HealthReadingListCreateView(generics.ListCreateAPIView):
    serializer_class = HealthReadingSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        patient_id = self.kwargs.get('patient_id')
        patient = get_object_or_404(PatientProfile, pk=patient_id)
        user = self.request.user
        if user.role in ('ADMIN', 'DOCTOR') or patient.user == user:
            return HealthReading.objects.filter(patient=patient)
        return HealthReading.objects.none()

    def perform_create(self, serializer):
        patient = get_object_or_404(PatientProfile, pk=self.kwargs['patient_id'])
        if self.request.user.role != 'ADMIN' and patient.user != self.request.user:
            raise PermissionDenied('You cannot add readings for another patient.')
        serializer.save(patient=patient)


class HealthReadingUploadView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, patient_id):
        patient = get_object_or_404(PatientProfile, pk=patient_id)
        if request.user.role != 'ADMIN' and patient.user != request.user:
            raise PermissionDenied('You cannot upload readings for another patient.')
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        decoded = file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        created = 0
        errors = []
        for idx, row in enumerate(reader, start=1):
            try:
                HealthReading.objects.create(
                    patient=patient,
                    heart_rate=int(row.get('heart_rate')) if row.get('heart_rate') else None,
                    blood_pressure_sys=int(row.get('blood_pressure_sys')) if row.get('blood_pressure_sys') else None,
                    blood_pressure_dia=int(row.get('blood_pressure_dia')) if row.get('blood_pressure_dia') else None,
                    oxygen_saturation=float(row.get('oxygen_saturation')) if row.get('oxygen_saturation') else None,
                    temperature=float(row.get('temperature')) if row.get('temperature') else None,
                    notes=row.get('notes', ''),
                )
                created += 1
            except Exception as e:
                errors.append({'row': idx, 'error': str(e)})

        return Response({'created': created, 'errors': errors}, status=status.HTTP_201_CREATED)
