# Generated by Django 3.0.3 on 2020-03-15 19:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ArquivoReferencia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=120, verbose_name='Nome do Arquivo Referencia')),
                ('arquivo', models.FileField(upload_to='pregacoes/arquivos/')),
            ],
            options={
                'verbose_name': 'Arquivo Pregação',
                'verbose_name_plural': 'Arquivos de Pregações',
                'db_table': 'pregacao_arquivos',
            },
        ),
        migrations.CreateModel(
            name='Local',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=120, verbose_name='Nome do Local')),
                ('endereco', models.CharField(max_length=230, verbose_name='Endereço do Local')),
            ],
            options={
                'verbose_name': 'Local Pregação',
                'verbose_name_plural': 'Locais de Pregação',
                'db_table': 'pregacao_local',
            },
        ),
        migrations.CreateModel(
            name='Preletor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=120, verbose_name='Nome do Local')),
                ('localidade', models.CharField(blank=True, max_length=120, null=True, verbose_name='Localidade Preletor')),
            ],
            options={
                'verbose_name': 'Preletor',
                'verbose_name_plural': 'Preletores',
                'db_table': 'pregacao_preletor',
            },
        ),
        migrations.CreateModel(
            name='Pregacao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=120, verbose_name='Titulo')),
                ('data_pregacao', models.DateField(verbose_name='Data da Pregação')),
                ('resumo', models.TextField(blank=True, null=True, verbose_name='Resumo Pregação')),
                ('arquivos', models.ManyToManyField(related_name='referencia_arquivos', to='pregacoes.ArquivoReferencia', verbose_name='Arquivos de Referência')),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='pregacoes.Local', verbose_name='Local da Pregação')),
                ('preletor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pregacoes.Preletor', verbose_name='Preletor')),
            ],
            options={
                'verbose_name': 'Pregação',
                'verbose_name_plural': 'Pregações',
                'db_table': 'pregacao_pregacao',
            },
        ),
        migrations.AddField(
            model_name='arquivoreferencia',
            name='pregacao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pregacao_arquivo_referencia', to='pregacoes.Pregacao', verbose_name='Pregação'),
        ),
    ]