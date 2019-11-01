# Generated by Django 2.2.5 on 2019-10-31 18:33

from django.conf import settings
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Nutrition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calories', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating_value', models.IntegerField()),
                ('review_body', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='RecipeAuthor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.URLField()),
                ('date_published', models.DateTimeField()),
                ('description', models.CharField(max_length=255)),
                ('prep_time', models.DurationField()),
                ('cook_time', models.DurationField()),
                ('recipe_yield', models.CharField(max_length=100)),
                ('recipe_category', models.CharField(max_length=100)),
                ('recipe_cuisine', models.CharField(max_length=100)),
                ('recipe_instructions', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), size=None)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='koocook_core.RecipeAuthor')),
                ('nutrition_info', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='koocook_core.Nutrition')),
                ('recipe_ingredient', models.ManyToManyField(to='koocook_core.Ingredient')),
                ('tags', models.ManyToManyField(to='koocook_core.Tag')),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='ingredient',
            name='nutrition',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='koocook_core.Nutrition'),
        ),
    ]
