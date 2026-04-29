from django.urls import path
from .views import (
    DepartmentListCreateView,
    OrderListCreateView,
    OrderDetailView,
    OrderExecuteView,
)

urlpatterns = [
    path('departments/', DepartmentListCreateView.as_view(), name='department-list-create'),
    path('', OrderListCreateView.as_view(), name='order-list-create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/execute/', OrderExecuteView.as_view(), name='order-execute'),
]
