from django.contrib import admin
from django.urls import include, path
from django.conf import settings

from .core import urls as core_urls

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path('', include(core_urls)),
]
