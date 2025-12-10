from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_remove_episode_title_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='season',
            name='episodes_count',
            field=models.IntegerField(default=0, help_text='Кількість епізодів у сезоні'),
        ),
        migrations.DeleteModel(
            name='Episode',
        ),
    ]
