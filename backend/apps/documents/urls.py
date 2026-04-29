from django.urls import path
from .views import DocumentListCreateView, DocumentDownloadView

urlpatterns = [
    path('', DocumentListCreateView.as_view(), name='document-list-create'),
    path('<int:pk>/download/', DocumentDownloadView.as_view(), name='document-download'),
]
