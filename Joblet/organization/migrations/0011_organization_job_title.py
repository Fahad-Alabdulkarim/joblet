# Generated by Django 5.1.2 on 2024-12-11 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0010_alter_organization_profile_completion'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='job_title',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
