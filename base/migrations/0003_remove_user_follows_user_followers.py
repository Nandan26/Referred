# Generated by Django 4.1.7 on 2023-06-04 16:39

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_remove_user_followers_user_follows'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='follows',
        ),
        migrations.AddField(
            model_name='user',
            name='followers',
            field=models.ManyToManyField(blank=True, related_name='following', to=settings.AUTH_USER_MODEL),
        ),
    ]
