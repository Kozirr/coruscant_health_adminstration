from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from .views import index, health
from apps.core.views import SystemStatusView

urlpatterns = [
    path('health/', health, name='health'),
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/patients/', include('apps.patients.urls')),
    path('api/v1/doctors/', include('apps.doctors.urls')),
    path('api/v1/orders/', include('apps.orders.urls')),
    path('api/v1/documents/', include('apps.documents.urls')),
    path('api/v1/emergency/', include('apps.emergency.urls')),
    path('api/v1/admin/system/', SystemStatusView.as_view(), name='system_status'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.FRONTEND_DIR.exists():
    urlpatterns += [re_path(r'^.*$', index)]
