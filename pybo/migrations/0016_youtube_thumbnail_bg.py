# Generated by Django 3.1.2 on 2021-01-26 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pybo', '0015_auto_20210125_1208'),
    ]

    operations = [
        migrations.AddField(
            model_name='youtube',
            name='thumbnail_bg',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]