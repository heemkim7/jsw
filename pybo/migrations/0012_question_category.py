# Generated by Django 3.1.2 on 2021-01-21 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pybo', '0011_keyword'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='category',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
