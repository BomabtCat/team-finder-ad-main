from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from projects.views import project_list_view

urlpatterns = [
    path("", lambda request: redirect("projects:list")),
    path("admin/", admin.site.urls),
    path("project/list", project_list_view),
    path("project/list/", project_list_view),
    path("projects/", include("projects.urls")),
    path("users/", include("users.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
