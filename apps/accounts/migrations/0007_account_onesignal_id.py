# Generated by Django 3.0.1 on 2020-01-13 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20200111_2216'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='onesignal_id',
            field=models.CharField(blank=True, max_length=120, null=True, verbose_name='ID OneSignal'),
        ),
    ]
