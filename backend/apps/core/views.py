import platform
import sys
from io import StringIO

from django import get_version as django_version
from django.core.management import call_command
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin


class SystemStatusView(APIView):
    permission_classes = (IsAdmin,)

    def get(self, request):
        out = StringIO()
        err = StringIO()
        try:
            call_command('migrate', '--check', stdout=out, stderr=err)
            migrations_ok = True
            migrations_msg = 'All migrations applied'
        except SystemExit:
            migrations_ok = False
            migrations_msg = 'Pending migrations detected'
        except Exception as e:
            migrations_ok = False
            migrations_msg = str(e)

        return Response({
            'db_connected': True,
            'migrations_status': migrations_msg,
            'migrations_ok': migrations_ok,
            'django_version': django_version(),
            'python_version': platform.python_version(),
        })
