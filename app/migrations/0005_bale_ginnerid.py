# Generated by Django 2.2.10 on 2021-06-15 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20210615_0315'),
    ]

    operations = [
        migrations.AddField(
            model_name='bale',
            name='ginnerid',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
