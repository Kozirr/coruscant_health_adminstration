from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from apps.patients.models import PatientProfile
from .models import EmergencyPatient
from .serializers import EmergencyPatientSerializer


class EmergencyPatientListCreateView(generics.ListCreateAPIView):
    serializer_class = EmergencyPatientSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.role in ('ADMIN', 'EMERGENCY'):
            return EmergencyPatient.objects.all()
        return EmergencyPatient.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role not in ('ADMIN', 'EMERGENCY'):
            raise PermissionDenied('Only emergency services can create emergency entries.')
        serializer.save(input_by=self.request.user)


class EmergencyPatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmergencyPatientSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.role in ('ADMIN', 'EMERGENCY'):
            return EmergencyPatient.objects.all()
        return EmergencyPatient.objects.none()


class ConvertEmergencyPatientView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        if request.user.role not in ('ADMIN', 'EMERGENCY'):
            raise PermissionDenied('Only emergency services can convert emergency entries.')
        emergency = get_object_or_404(EmergencyPatient, pk=pk)
        if emergency.converted_to_patient:
            return Response({'detail': 'Already converted.'}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            username=f"emerg_{emergency.id}_{emergency.last_name.lower()}",
            first_name=emergency.first_name,
            last_name=emergency.last_name,
            role='PATIENT',
            password=None,
        )
        PatientProfile.objects.create(user=user)
        emergency.converted_to_patient = True
        emergency.save()
        return Response({'detail': 'Converted to patient.', 'user_id': user.id}, status=status.HTTP_201_CREATED)
