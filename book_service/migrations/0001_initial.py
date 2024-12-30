# Generated by Django 5.1.4 on 2024-12-18 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("author", models.CharField(max_length=255)),
                ("cover", models.IntegerField(choices=[(0, "Soft"), (1, "Hard")])),
                ("inventory", models.IntegerField(default=0)),
                ("fee", models.IntegerField()),
            ],
        ),
    ]
