# Generated by Django 5.1.4 on 2024-12-19 09:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("book_service", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BorrowingService",
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
                ("borrow_date", models.DateField()),
                ("expected_return", models.DateField()),
                ("actual_return", models.DateField(blank=True, null=True)),
                (
                    "book",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="book_service.book",
                    ),
                ),
            ],
        ),
    ]