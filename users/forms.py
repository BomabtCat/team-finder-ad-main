from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from team_finder.utils import validate_github_url

from .models import User
from .utils import (
    RUSSIAN_INTERNATIONAL_PHONE_LENGTH,
    RUSSIAN_INTERNATIONAL_PHONE_PREFIX,
    normalize_phone,
)


PROFILE_ABOUT_WIDGET_ROWS = 5


class RegisterForm(forms.ModelForm):
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class EmailLoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user_cache = None

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            self.user_cache = authenticate(
                self.request, username=email, password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError("Неверный email или пароль.")
        return cleaned_data

    def get_user(self):
        return self.user_cache


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["avatar", "name", "surname", "about", "phone", "github_url"]
        labels = {
            "avatar": "Аватар",
            "name": "Имя",
            "surname": "Фамилия",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "GitHub",
        }
        widgets = {
            "about": forms.Textarea(attrs={"rows": PROFILE_ABOUT_WIDGET_ROWS}),
        }

    def clean_phone(self):
        phone = normalize_phone(self.cleaned_data["phone"])
        if not phone:
            raise forms.ValidationError("Телефон обязателен.")
        phone_digits = phone[len(RUSSIAN_INTERNATIONAL_PHONE_PREFIX):]
        if (
            not phone.startswith(RUSSIAN_INTERNATIONAL_PHONE_PREFIX)
            or len(phone) != RUSSIAN_INTERNATIONAL_PHONE_LENGTH
            or not phone_digits.isdigit()
        ):
            raise forms.ValidationError(
                "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX."
            )
        users = User.objects.filter(phone=phone)
        if self.instance.pk:
            users = users.exclude(pk=self.instance.pk)
        if users.exists():
            raise forms.ValidationError("Пользователь с таким телефоном уже существует.")
        return phone

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url", "")
        validate_github_url(github_url)
        return github_url


class UserPasswordChangeForm(PasswordChangeForm):
    pass
