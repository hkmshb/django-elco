# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_auto_20151111_1049'),
    ]

    operations = [
        migrations.AlterField(
            model_name='station',
            name='source_feeder',
            field=models.ForeignKey(verbose_name='Source Feeder', null=True, to='network.PowerLine', default=None, blank=True, on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
