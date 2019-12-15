# Generated by Django 2.2.7 on 2019-12-13 07:14

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import koocook_auth.models
import koocook_core.models.base


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='KoocookUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preferences', django.contrib.postgres.fields.jsonb.JSONField(default=koocook_auth.models._default_preferences)),
                ('user_settings', django.contrib.postgres.fields.jsonb.JSONField(default=koocook_auth.models._default_preferences)),
                ('followers', models.ManyToManyField(related_name='_koocookuser_followers_+', to='koocook_auth.KoocookUser')),
                ('following', models.ManyToManyField(related_name='_koocookuser_following_+', to='koocook_auth.KoocookUser')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'koocook_auth_user',
            },
            bases=(koocook_core.models.base.SerialisableModel, models.Model),
        ),
    ]
