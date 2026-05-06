from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0002_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="skill",
            name="name",
            field=models.CharField(max_length=124, unique=True, verbose_name="Название"),
        ),
        migrations.AlterField(
            model_name="project",
            name="description",
            field=models.TextField(blank=True, verbose_name="Описание"),
        ),
        migrations.AlterField(
            model_name="project",
            name="status",
            field=models.CharField(
                choices=[("open", "Open"), ("closed", "Closed")],
                default="open",
                max_length=6,
                verbose_name="Статус",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="participants",
            field=models.ManyToManyField(
                blank=True,
                related_name="participated_projects",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
