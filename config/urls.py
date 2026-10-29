import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# L'URL de l'admin est configurable pour éviter les robots qui visent /admin/.
ADMIN_URL = os.getenv("ADMIN_URL", "admin/")

urlpatterns = [
    path(ADMIN_URL, admin.site.urls),
    path("", include("portfolio.urls")),
]

# En production, PythonAnywhere sert /media/ directement (onglet Web).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
