from django.conf import settings
from django.db import models
from django.urls import reverse


SKILL_NAME_MAX_LENGTH = 124
PROJECT_NAME_MAX_LENGTH = 200
PROJECT_STATUS_MAX_LENGTH = 6


class Skill(models.Model):
    name = models.CharField("Название", max_length=SKILL_NAME_MAX_LENGTH, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_CLOSED, "Closed"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор",
    )
    name = models.CharField("Название", max_length=PROJECT_NAME_MAX_LENGTH)
    description = models.TextField("Описание", blank=True)
    github_url = models.URLField("GitHub", blank=True)
    status = models.CharField(
        "Статус",
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="participated_projects", blank=True
    )
    favorites = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="favorite_projects", blank=True
    )
    skills = models.ManyToManyField(Skill, related_name="projects", blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("projects:detail", kwargs={"pk": self.pk})
