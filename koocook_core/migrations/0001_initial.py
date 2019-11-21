# Generated by Django 2.2.7 on 2019-11-21 05:54

from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import koocook_core.models.base
import koocook_core.models.review
import koocook_core.models.user
import koocook_core.support.quantity


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AggregateRating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating_value', models.DecimalField(decimal_places=10, max_digits=13)),
                ('rating_count', models.IntegerField()),
                ('best_rating', models.IntegerField(default=5)),
                ('worst_rating', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            bases=(koocook_core.models.base.SerialisableModel, models.Model),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_published', models.DateTimeField()),
                ('body', models.TextField()),
                ('aggregate_rating', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='koocook_core.AggregateRating')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='koocook_core.Author')),
                ('reviewed_comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='koocook_core.Comment')),
            ],
        ),
        migrations.CreateModel(
            name='MetaIngredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('nutrient', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_published', models.DateTimeField(auto_now_add=True)),
                ('body', models.TextField()),
                ('aggregate_rating', models.OneToOneField(blank=True, default=koocook_core.models.review.create_empty_aggregate_rating, on_delete=django.db.models.deletion.PROTECT, to='koocook_core.AggregateRating')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='koocook_core.Author')),
            ],
            bases=(koocook_core.models.base.SerialisableModel, models.Model),
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('image', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), null=True, size=None)),
                ('video', models.URLField(blank=True, null=True)),
                ('date_published', models.DateTimeField(null=True)),
                ('description', models.TextField()),
                ('prep_time', models.DurationField(blank=True, null=True)),
                ('cook_time', models.DurationField(null=True)),
                ('recipe_instructions', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), size=None)),
                ('recipe_yield', koocook_core.support.quantity.QuantityField(null=True)),
                ('aggregate_rating', models.OneToOneField(blank=True, default=koocook_core.models.review.create_empty_aggregate_rating, on_delete=django.db.models.deletion.PROTECT, to='koocook_core.AggregateRating')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='koocook_core.Author')),
            ],
        ),
        migrations.CreateModel(
            name='TagLabel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('label', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='koocook_core.TagLabel')),
            ],
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', koocook_core.support.quantity.QuantityField()),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('meta', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='koocook_core.MetaIngredient')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='koocook_core.Recipe')),
                ('substitute_set', models.ManyToManyField(blank=True, related_name='_recipeingredient_substitute_set_+', to='koocook_core.RecipeIngredient')),
            ],
        ),
        migrations.AddField(
            model_name='recipe',
            name='tag_set',
            field=models.ManyToManyField(blank=True, to='koocook_core.Tag'),
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating_value', models.IntegerField()),
                ('best_rating', models.IntegerField(default=5)),
                ('worst_rating', models.IntegerField(default=1)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='koocook_core.Author')),
                ('reviewed_comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='koocook_core.Comment')),
                ('reviewed_post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='koocook_core.Post')),
                ('reviewed_recipe', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='koocook_core.Recipe')),
            ],
        ),
        migrations.CreateModel(
            name='KoocookUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preferences', django.contrib.postgres.fields.jsonb.JSONField(default=koocook_core.models.user._default_preferences)),
                ('user_settings', django.contrib.postgres.fields.jsonb.JSONField(default=koocook_core.models.user._default_preferences)),
                ('followers', models.ManyToManyField(related_name='_koocookuser_followers_+', to='koocook_core.KoocookUser')),
                ('following', models.ManyToManyField(related_name='_koocookuser_following_+', to='koocook_core.KoocookUser')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'koocook_user',
            },
            bases=(koocook_core.models.base.SerialisableModel, models.Model),
        ),
        migrations.AddField(
            model_name='comment',
            name='reviewed_post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='koocook_core.Post'),
        ),
        migrations.AddField(
            model_name='comment',
            name='reviewed_recipe',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='koocook_core.Recipe'),
        ),
        migrations.AddField(
            model_name='author',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='koocook_core.KoocookUser'),
        ),
    ]
