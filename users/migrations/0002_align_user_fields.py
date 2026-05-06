from django.db import migrations, models


def fill_required_user_fields(apps, schema_editor):
    User = apps.get_model("users", "User")
    for user in User.objects.all():
        changed = False
        if not user.phone:
            user.phone = f"+7900{user.pk:07d}"
            changed = True
        elif user.phone.startswith("8") and len(user.phone) == 11:
            user.phone = "+7" + user.phone[1:]
            changed = True
        if not user.avatar:
            user.avatar = "avatars/default-avatar.png"
            changed = True
        if changed:
            user.save(update_fields=["phone", "avatar"])


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="name",
            field=models.CharField(max_length=124, verbose_name="Имя"),
        ),
        migrations.AlterField(
            model_name="user",
            name="surname",
            field=models.CharField(max_length=124, verbose_name="Фамилия"),
        ),
        migrations.AlterField(
            model_name="user",
            name="about",
            field=models.TextField(blank=True, max_length=256, verbose_name="О себе"),
        ),
        migrations.RunPython(fill_required_user_fields, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="avatar",
            field=models.ImageField(upload_to="avatars/", verbose_name="Аватар"),
        ),
        migrations.AlterField(
            model_name="user",
            name="phone",
            field=models.CharField(max_length=12, unique=True, verbose_name="Телефон"),
        ),
    ]
