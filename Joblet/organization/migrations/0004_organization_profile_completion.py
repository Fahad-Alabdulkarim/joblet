# Generated by Django 5.1.2 on 2024-12-10 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0003_alter_organization_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='profile_completion',
            field=models.SmallIntegerField(default=10),
        ),
    ]