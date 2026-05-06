from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from .utils import (
    generate_avatar,
    generate_avatar_name,
    generate_placeholder_phone,
    normalize_phone,
)


USERNAME_MAX_LENGTH = 150
USER_NAME_MAX_LENGTH = 124
USER_ABOUT_MAX_LENGTH = 256
USER_PHONE_MAX_LENGTH = 12


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("name", "Admin")
        extra_fields.setdefault("surname", "User")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=USERNAME_MAX_LENGTH, blank=True)
    email = models.EmailField("email", unique=True)
    name = models.CharField("Имя", max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField("Фамилия", max_length=USER_NAME_MAX_LENGTH)
    avatar = models.ImageField("Аватар", upload_to="avatars/")
    about = models.TextField("О себе", max_length=USER_ABOUT_MAX_LENGTH, blank=True)
    phone = models.CharField("Телефон", max_length=USER_PHONE_MAX_LENGTH, unique=True)
    github_url = models.URLField("GitHub", blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.phone:
            self.phone = generate_placeholder_phone(self.email, type(self))
        if self.phone:
            self.phone = normalize_phone(self.phone)
        if not self.avatar:
            self.avatar.save(
                generate_avatar_name(self),
                generate_avatar(self),
                save=False,
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.surname}".strip() or self.email
