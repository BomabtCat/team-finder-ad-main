from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from team_finder.utils import get_json_body, paginate_queryset

from .forms import ProjectForm
from .models import Project, Skill


SKILLS_SUGGEST_LIMIT = 10


def project_list_view(request):
    active_skill = request.GET.get("skill")
    projects = Project.objects.select_related("owner").prefetch_related(
        "participants", "skills"
    )
    if active_skill:
        projects = projects.filter(skills__name=active_skill)
    page_obj = paginate_queryset(request, projects.distinct())
    all_skills = Skill.objects.values_list("name", flat=True).order_by("name")
    return render(
        request,
        "projects/project_list.html",
        {
            "projects": page_obj.object_list,
            "page_obj": page_obj,
            "all_skills": all_skills,
            "active_skill": active_skill,
        },
    )


def project_detail_view(request, pk):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related(
            "participants", "skills"
        ),
        pk=pk,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project_view(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect(project)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False},
    )


@login_required
def edit_project_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.owner and not request.user.is_staff:
        return redirect(project)
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(project)
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True, "project": project},
    )


@login_required
def favorite_projects_view(request):
    projects = request.user.favorite_projects.select_related("owner").prefetch_related(
        "participants", "skills"
    )
    return render(request, "projects/favorite_projects.html", {"projects": projects})


@login_required
@require_POST
def complete_project_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.owner and not request.user.is_staff:
        return JsonResponse({"status": "forbidden"}, status=HTTPStatus.FORBIDDEN)
    if project.status != Project.STATUS_OPEN:
        return JsonResponse({"status": "bad_request"}, status=HTTPStatus.BAD_REQUEST)
    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status", "updated_at"])
    return JsonResponse({"status": "ok", "project_status": Project.STATUS_CLOSED})


@login_required
@require_POST
def toggle_participate_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user == project.owner:
        return JsonResponse({"status": "forbidden"}, status=HTTPStatus.FORBIDDEN)
    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True
    return JsonResponse({"status": "ok", "participant": participant})


@login_required
@require_POST
def toggle_favorite_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.favorites.filter(pk=request.user.pk).exists():
        project.favorites.remove(request.user)
        favorited = False
    else:
        project.favorites.add(request.user)
        favorited = True
    return JsonResponse({"status": "ok", "favorited": favorited})


@require_GET
def skills_suggest_view(request):
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.all()
    if query:
        skills = skills.filter(name__istartswith=query)
    data = [
        {"id": skill.id, "name": skill.name}
        for skill in skills[:SKILLS_SUGGEST_LIMIT]
    ]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_project_skill_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.owner and not request.user.is_staff:
        return JsonResponse({"status": "forbidden"}, status=HTTPStatus.FORBIDDEN)

    payload = get_json_body(request)
    skill = None
    skill_id = payload.get("skill_id") or request.POST.get("skill_id")
    name = (payload.get("name") or request.POST.get("name") or "").strip()
    created = False
    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({"status": "bad_request"}, status=HTTPStatus.BAD_REQUEST)

    added = not project.skills.filter(pk=skill.pk).exists()
    project.skills.add(skill)
    return JsonResponse(
        {
            "id": skill.id,
            "name": skill.name,
            "skill_id": skill.id,
            "created": created,
            "added": added,
        }
    )


@login_required
@require_POST
def remove_project_skill_view(request, pk, skill_id):
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.owner and not request.user.is_staff:
        return JsonResponse({"status": "forbidden"}, status=HTTPStatus.FORBIDDEN)
    skill = get_object_or_404(Skill, pk=skill_id)
    if not project.skills.filter(pk=skill.pk).exists():
        return JsonResponse({"status": "bad_request"}, status=HTTPStatus.BAD_REQUEST)
    project.skills.remove(skill)
    return JsonResponse({"status": "ok"})
