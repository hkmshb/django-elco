# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_auto_20151119_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transformer',
            name='condition',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Unknown'), (2, 'OK'), (3, 'Faulty'), (4, 'Damaged')], verbose_name='Condition'),
        ),
    ]
