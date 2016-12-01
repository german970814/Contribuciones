# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Observacion',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('texto', models.TextField(verbose_name='observacion')),
            ],
            options={
                'verbose_name': 'Observacion',
                'verbose_name_plural': 'Observaciones',
            },
        ),
        migrations.CreateModel(
            name='Persona',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('nombre', models.CharField(max_length=255, verbose_name='nombre')),
                ('primer_apellido', models.CharField(max_length=255, verbose_name='primer apellido')),
                ('segundo_apellido', models.CharField(blank=True, max_length=255, verbose_name='segundo apellido')),
                ('cedula', models.BigIntegerField(unique=True, verbose_name='no. identificación')),
                ('telefono', models.BigIntegerField(blank=True, null=True, verbose_name='teléfono')),
            ],
            options={
                'verbose_name': 'Persona',
                'verbose_name_plural': 'Personas',
            },
        ),
        migrations.CreateModel(
            name='Sobre',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('fecha', models.DateField(verbose_name='fecha')),
                ('diligenciado', models.BooleanField(verbose_name='sobre diligenciado', default=True)),
                ('valor', models.BigIntegerField(verbose_name='valor')),
                ('forma_pago', models.CharField(max_length=2, choices=[('EF', 'EFECTIVO'), ('CH', 'CHEQUE'), ('EL', 'ELECTRONICO')], verbose_name='forma de pago')),
                ('persona', models.ForeignKey(null=True, to='main.Persona', blank=True, verbose_name='persona', related_name='sobres')),
            ],
            options={
                'verbose_name': 'Sobre',
                'verbose_name_plural': 'Sobres',
            },
        ),
        migrations.CreateModel(
            name='TipoIngreso',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('nombre', models.CharField(max_length=255, verbose_name='nombre')),
            ],
            options={
                'verbose_name': 'Tipo Ingreso',
                'verbose_name_plural': 'Tipos de Ingreso',
            },
        ),
        migrations.AddField(
            model_name='sobre',
            name='tipo_ingreso',
            field=models.ForeignKey(verbose_name='tipo ingreso', to='main.TipoIngreso', related_name='sobres'),
        ),
    ]
