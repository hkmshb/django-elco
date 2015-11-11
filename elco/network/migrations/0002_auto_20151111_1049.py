# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import elco.network.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transformer',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('is_active', models.BooleanField(db_index=True, verbose_name='Active', default=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('last_updated', models.DateTimeField(null=True, verbose_name='Last Updated', auto_now=True)),
                ('serialno', models.CharField(blank=True, max_length=50, unique=True, verbose_name='Serial #')),
                ('model', models.CharField(blank=True, max_length=100, verbose_name='Model')),
                ('manufacturer', models.CharField(blank=True, max_length=100, verbose_name='Manufacturer')),
                ('condition', models.PositiveSmallIntegerField(choices=[(1, 'Unknown'), (2, 'OK'), (3, 'Faulty'), (4, 'DAMAGED')], verbose_name='Condition')),
                ('date_installed', models.DateField(blank=True, null=True, verbose_name='Date Installed')),
                ('date_manufactured', models.DateField(blank=True, null=True, verbose_name='Date Manufactured')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TransformerRating',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('is_active', models.BooleanField(db_index=True, verbose_name='Active', default=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date Created')),
                ('last_updated', models.DateTimeField(null=True, verbose_name='Last Updated', auto_now=True)),
                ('code', models.CharField(max_length=5, unique=True, verbose_name='Code', validators=[elco.network.validators.validate_transformer_rating_code_format])),
                ('capacity', models.PositiveIntegerField(verbose_name='Capacity')),
                ('voltage_ratio', models.PositiveSmallIntegerField(choices=[(1, '330/132KV'), (2, '132/33KV'), (4, '33/11KV'), (5, '33/0.415KV'), (6, '11/0.415KV')], verbose_name='Voltage Ratio')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='transformerrating',
            unique_together=set([('capacity', 'voltage_ratio')]),
        ),
        migrations.AddField(
            model_name='transformer',
            name='rating',
            field=models.ForeignKey(verbose_name='Rating', to_field='code', to='network.TransformerRating', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='transformer',
            name='station',
            field=models.ForeignKey(verbose_name='Station', to_field='code', to='network.Station', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
