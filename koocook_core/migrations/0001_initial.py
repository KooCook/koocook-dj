# Generated by Django 3.0 on 2019-12-16 01:47

import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import koocook_core.models.base
import koocook_core.models.review
import koocook_core.support.markdown
import koocook_core.support.quantity


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('koocook_auth', '0001_initial'),
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
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='koocook_auth.KoocookUser')),
            ],
            bases=(koocook_core.models.base.SerialisableModel, models.Model),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_published', models.DateTimeField(auto_now_add=True)),
                ('body', koocook_core.support.markdown.FormattedField()),
                ('aggregate_rating', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='koocook_core.AggregateRating')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='koocook_core.Author')),
                ('reviewed_comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='koocook_core.Comment')),
            ],
            bases=(koocook_core.models.review.ReviewerModel, koocook_core.models.base.SerialisableModel, koocook_core.models.review.ReviewableModel, models.Model),
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
                ('body', koocook_core.support.markdown.FormattedField()),
                ('aggregate_rating', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.PROTECT, to='koocook_core.AggregateRating')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='koocook_core.Author')),
            ],
            bases=(koocook_core.models.base.SerialisableModel, koocook_core.models.review.ReviewableModel, models.Model),
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('image', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, null=True, size=None)),
                ('video', models.URLField(blank=True, null=True)),
                ('date_published', models.DateTimeField(auto_now_add=True, null=True)),
                ('description', models.TextField()),
                ('prep_time', models.DurationField(null=True)),
                ('cook_time', models.DurationField(null=True)),
                ('recipe_instructions', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), default=list, size=None)),
                ('recipe_yield', koocook_core.support.quantity.QuantityField(null=True)),
                ('aggregate_rating', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.PROTECT, to='koocook_core.AggregateRating')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='koocook_core.Author')),
            ],
            bases=(koocook_core.models.review.ReviewableModel, models.Model),
        ),
        migrations.CreateModel(
            name='RecipeEquipment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            bases=(koocook_core.models.base.SerialisableModel, models.Model),
        ),
        migrations.CreateModel(
            name='TagLabel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('level', models.IntegerField(default=1)),
            ],
            bases=(koocook_core.models.base.SerialisableModel, models.Model),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('label', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='koocook_core.TagLabel')),
            ],
            options={
                'unique_together': {('name', 'label')},
            },
            bases=(koocook_core.models.base.SerialisableModel, models.Model),
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
            name='equipment_set',
            field=models.ManyToManyField(blank=True, to='koocook_core.RecipeEquipment'),
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
                ('used', models.BooleanField(blank=True, default=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='koocook_core.Author')),
                ('reviewed_comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='koocook_core.Comment')),
                ('reviewed_post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='koocook_core.Post')),
                ('reviewed_recipe', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='koocook_core.Recipe')),
            ],
            bases=(koocook_core.models.review.ReviewerModel, models.Model),
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_published', models.DateTimeField(auto_now_add=True)),
                ('subject', models.CharField(max_length=100)),
                ('body', models.TextField()),
                ('image', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, null=True, size=None)),
                ('video', models.URLField(blank=True, null=True)),
                ('status', models.BooleanField(default=False)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='koocook_core.Author')),
            ],
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
        migrations.CreateModel(
            name='RecipeVisit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.CharField(max_length=45)),
                ('date_first_visited', models.DateTimeField(auto_now_add=True)),
                ('date_last_visited', models.DateTimeField(auto_now=True)),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='koocook_core.Recipe')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='koocook_auth.KoocookUser')),
            ],
            options={
                'verbose_name': 'Recipe visit count',
                'db_table': 'koocook_core_recipe_visit',
                'unique_together': {('user', 'recipe'), ('ip_address', 'user', 'recipe')},
            },
        ),
    ]
