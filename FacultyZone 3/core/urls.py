from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # This line connects Django's built-in login/logout system
    path('accounts/', include('django.contrib.auth.urls')), 
    path('', include('academic.urls')),
]

# This allows Django to serve uploaded files (PDFs/Images) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)