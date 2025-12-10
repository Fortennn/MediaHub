from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('catalog', '0003_remove_episode_add_episodes_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RunPython(
            code=lambda apps, schema_editor: create_profiles(apps),
            reverse_code=migrations.RunPython.noop,
        ),
    ]


def create_profiles(apps):
    User = apps.get_model(settings.AUTH_USER_MODEL)
    Profile = apps.get_model('catalog', 'Profile')
    for user in User.objects.all():
        Profile.objects.get_or_create(user=user)
