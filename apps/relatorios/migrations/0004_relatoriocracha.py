# Generated by Django 3.0.3 on 2020-02-20 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('relatorios', '0003_relatoriohospedagem'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelatorioCracha',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Relatório para Cracha',
                'verbose_name_plural': 'Relatórios para Crachas',
                'db_table': 'relatorio_cach',
            },
        ),
    ]
