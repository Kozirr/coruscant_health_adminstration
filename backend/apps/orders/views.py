from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Department, Order
from .serializers import DepartmentSerializer, OrderSerializer


class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = (permissions.IsAuthenticated,)


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        qs = Order.objects.all()
        patient_id = self.request.query_params.get('patient')
        status_filter = self.request.query_params.get('status')
        if patient_id:
            qs = qs.filter(patient_id=patient_id)
        if status_filter:
            qs = qs.filter(status=status_filter.upper())
        return qs

    def perform_create(self, serializer):
        from apps.doctors.models import DoctorProfile
        doctor = get_object_or_404(DoctorProfile, user=self.request.user)
        serializer.save(doctor=doctor)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)


class OrderExecuteView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        order.status = request.data.get('status', 'IN_PROGRESS')
        if 'result_notes' in request.data:
            order.result_notes = request.data['result_notes']
        if 'result_file' in request.FILES:
            order.result_file = request.FILES['result_file']
        order.save()
        return Response(OrderSerializer(order).data)
