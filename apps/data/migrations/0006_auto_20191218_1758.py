# Generated by Django 2.2.6 on 2019-12-18 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0005_contato'),
    ]

    operations = [
        migrations.AddField(
            model_name='conferencia',
            name='endereco',
            field=models.CharField(blank=True, max_length=160, verbose_name='Endereço (googlemaps)'),
        ),
        migrations.AddField(
            model_name='conferencia',
            name='informacoes',
            field=models.TextField(blank=True, verbose_name='Informações Gerais'),
        ),
    ]