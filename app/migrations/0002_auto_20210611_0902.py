# Generated by Django 2.2.10 on 2021-06-11 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bale',
            old_name='Asking_Price',
            new_name='Spot_Price',
        ),
        migrations.AddField(
            model_name='bale',
            name='Available_For_Sale',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='bale',
            name='BCI',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='bale',
            name='GTex',
            field=models.CharField(default=100, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bale',
            name='Organic',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='bale',
            name='Rd',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='bale',
            name='Staple',
            field=models.CharField(default=100, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='testbale',
            name='test_by_fc',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='testbale',
            name='test_report',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
