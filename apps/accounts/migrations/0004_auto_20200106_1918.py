# Generated by Django 3.0.1 on 2020-01-06 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20200106_1846'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='username',
            field=models.CharField(blank=True, max_length=120, null=True, unique=True, verbose_name='User Name'),
        ),
    ]
