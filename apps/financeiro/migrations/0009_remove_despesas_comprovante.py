# Generated by Django 3.0.1 on 2020-01-28 00:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0008_comprovantes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='despesas',
            name='comprovante',
        ),
    ]
