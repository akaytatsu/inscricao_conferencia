# Generated by Django 3.0.1 on 2019-12-23 13:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('data', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriaDespesa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=80, verbose_name='Nome')),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Categoria Despesa',
                'verbose_name_plural': 'Categorias Despesa',
                'db_table': 'categoria_despesa',
            },
        ),
        migrations.CreateModel(
            name='Receitas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_receita', models.IntegerField(choices=[(1, 'PagSeguro'), (2, 'Oferta'), (3, 'Outro')], default=1, verbose_name='Tipo de Receita')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Valor')),
                ('data_receita', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Data Receita')),
            ],
            options={
                'verbose_name': 'Receita',
                'verbose_name_plural': 'Receitas',
            },
        ),
        migrations.CreateModel(
            name='Despesas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Solicitação'), (2, 'Aprovada'), (3, 'Comprovação')], default=1, verbose_name='Status')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Valor')),
                ('justificativa', models.CharField(max_length=500, verbose_name='Justificativa')),
                ('aprovado', models.BooleanField(default=False, verbose_name='Aprovado?')),
                ('comprovado', models.BooleanField(default=False, verbose_name='Comprovado?')),
                ('categoria', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='financeiro.CategoriaDespesa', verbose_name='Categoria de Despesa')),
                ('conferencia', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='data.Conferencia', verbose_name='Conferencia')),
                ('usuario_aprovacao', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='usuario_aprovacao', to=settings.AUTH_USER_MODEL, verbose_name='Usuario Aprovação')),
                ('usuario_comprovacao', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='usuario_comprovacao', to=settings.AUTH_USER_MODEL, verbose_name='Usuario Comprovação')),
                ('usuario_solicitacao', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='usuario_solicitacao', to=settings.AUTH_USER_MODEL, verbose_name='Usuario Solicitação')),
            ],
            options={
                'verbose_name': 'Despesa',
                'verbose_name_plural': 'Despesas',
                'db_table': 'despesas',
            },
        ),
    ]
