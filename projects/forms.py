from django import forms

from team_finder.utils import validate_github_url

from .models import Project


DESCRIPTION_WIDGET_ROWS = 6


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        labels = {
            "name": "Название",
            "description": "Описание",
            "github_url": "GitHub",
            "status": "Статус",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": DESCRIPTION_WIDGET_ROWS}),
        }

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url", "")
        validate_github_url(github_url)
        return github_url
