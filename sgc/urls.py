"""
URL configuration for sgc project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView, RedirectView
from django.views.static import serve
from django.http import Http404
import os

_DOCS_ROOT = os.path.join(settings.BASE_DIR, 'docs_site')

def serve_docs(request, path):
    """Sirve el sitio MkDocs resolviendo index.html en directorios."""
    if not path or path.endswith('/'):
        path = path + 'index.html'
    full = os.path.join(_DOCS_ROOT, path)
    if os.path.isdir(full):
        path = path.rstrip('/') + '/index.html'
    return serve(request, path, document_root=_DOCS_ROOT, show_indexes=False)

urlpatterns = [
    # Compatibilidad para URLs malformadas con comillas codificadas (%22 ... %22).
    re_path(
        r'^"/nc/normas/(?P<norma_id>\d+)/puntos/lista//"$',
        RedirectView.as_view(url='/nc/normas/%(norma_id)s/puntos/lista/', permanent=False),
    ),
    re_path(
        r'^"/nc/normas/(?P<norma_id>\d+)/puntos/nuevo//"$',
        RedirectView.as_view(url='/nc/normas/%(norma_id)s/puntos/nuevo/', permanent=False),
    ),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('admin/', admin.site.urls),
    path('core/', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('nc/', include('apps.nc.urls')),
    path('qr/', include('apps.qr.urls')),
    path('om/', include('apps.om.urls')),
    path('proyectos/', include('apps.proyectos.urls')),
    path('verificacion/', include('apps.verificacion.urls')),
    path('notificaciones/', include('apps.notificaciones.urls')),
    path('reportes/', include('apps.reportes.urls')),
    path('backups/', include('apps.backups.urls')),
    # Documentación MkDocs servida internamente (resuelve index.html en directorios)
    re_path(r'^docs/(?P<path>.*)$', serve_docs),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

