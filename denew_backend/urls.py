from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('accounts.urls')),  # Root includes accounts app; consider a specific root view
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
  static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Notes for production:
# - Remove static() and media() calls; use a web server (e.g., Nginx) or Whitenoise
# - Example with Whitenoise: Add 'whitenoise.runserver_nostatic' to MIDDLEWARE in settings.py
# - For media in production, use a storage backend (e.g., AWS S3) instead of serving directly