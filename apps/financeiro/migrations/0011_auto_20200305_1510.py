# Generated by Django 3.0.3 on 2020-03-05 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0010_auto_20200212_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comprovantes',
            name='comprovante',
            field=models.FileField(blank=True, null=True, upload_to='comprovantes/'),
        ),
    ]