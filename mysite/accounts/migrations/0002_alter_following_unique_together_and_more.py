# Generated by Django 4.0.6 on 2022-09-04 19:59

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='following',
            unique_together={('follower', 'followed')},
        ),
        migrations.RemoveField(
            model_name='following',
            name='following',
        ),
    ]
