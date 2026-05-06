from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from team_finder.utils import paginate_queryset

from .forms import EmailLoginForm, ProfileForm, RegisterForm, UserPasswordChangeForm
from .models import User


def register_view(request):
    if request.user.is_authenticated:
        return redirect("projects:list")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("users:login")
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("projects:list")
    form = EmailLoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get("next") or "projects:list")
    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


def participants_view(request):
    participants = User.objects.order_by("-date_joined")
    page_obj = paginate_queryset(request, participants)
    return render(
        request,
        "users/participants.html",
        {"participants": page_obj.object_list, "page_obj": page_obj},
    )


def profile_view(request, pk):
    profile_user = get_object_or_404(User, pk=pk)
    return render(request, "users/user-details.html", {"user": profile_user})


@login_required
def edit_profile_view(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("users:profile", pk=request.user.pk)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password_view(request):
    form = UserPasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("users:profile", pk=request.user.pk)
    return render(request, "users/change_password.html", {"form": form})
