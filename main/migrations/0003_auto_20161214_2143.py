# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_sobre_observaciones'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persona',
            name='cedula',
            field=models.BigIntegerField(unique=True, verbose_name='Identificación'),
        ),
    ]
