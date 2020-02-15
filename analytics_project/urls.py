from django.contrib import admin
from django.urls import include, path

from analytics import urls as analytics_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(analytics_urls)),
]
