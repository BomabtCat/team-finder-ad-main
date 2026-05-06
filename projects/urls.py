from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("list", views.project_list_view, name="list"),
    path("list/", views.project_list_view),
    path("create-project", views.create_project_view, name="create"),
    path("create-project/", views.create_project_view),
    path("favorites/", views.favorite_projects_view, name="favorites"),
    path("skills/", views.skills_suggest_view, name="skills"),
    path("<int:pk>", views.project_detail_view, name="detail"),
    path("<int:pk>/", views.project_detail_view),
    path("<int:pk>/edit", views.edit_project_view, name="edit"),
    path("<int:pk>/edit/", views.edit_project_view),
    path("<int:pk>/complete/", views.complete_project_view, name="complete"),
    path(
        "<int:pk>/toggle-participate/",
        views.toggle_participate_view,
        name="toggle_participate",
    ),
    path("<int:pk>/toggle-favorite/", views.toggle_favorite_view, name="toggle_favorite"),
    path("<int:pk>/skills/add/", views.add_project_skill_view, name="add_skill"),
    path(
        "<int:pk>/skills/<int:skill_id>/remove/",
        views.remove_project_skill_view,
        name="remove_skill",
    ),
]
