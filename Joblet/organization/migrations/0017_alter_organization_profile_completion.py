# Generated by Django 5.1.2 on 2024-12-17 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0016_remove_projects_likes_delete_organizationlike'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='profile_completion',
            field=models.SmallIntegerField(default=10),
        ),
    ]