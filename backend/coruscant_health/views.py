import os
from django.http import HttpResponse, JsonResponse
from django.conf import settings


def index(request):
    frontend_dir = settings.BASE_DIR.parent / 'frontend' / 'dist'
    index_path = frontend_dir / 'index.html'
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read())
    return HttpResponse("Frontend not built. Run npm run build in the frontend directory.", status=404)


def health(request):
    return JsonResponse({'status': 'ok'})
