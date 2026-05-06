import json

from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.validators import URLValidator


PROJECTS_PER_PAGE = 12
GITHUB_DOMAIN = "github.com"


def paginate_queryset(request, queryset, per_page=PROJECTS_PER_PAGE):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


def validate_github_url(value):
    if not value:
        return
    URLValidator()(value)
    if GITHUB_DOMAIN not in value.lower().split("/")[2]:
        raise ValidationError("Ссылка должна вести на GitHub.")


def get_json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return {}
