# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PowerLine',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('is_active', models.BooleanField(verbose_name='Active', db_index=True, default=True)),
                ('date_created', models.DateTimeField(verbose_name='Date Created', auto_now_add=True)),
                ('last_updated', models.DateTimeField(verbose_name='Last Updated', null=True, auto_now=True)),
                ('code', models.CharField(verbose_name='Code', max_length=10, unique=True)),
                ('name', models.CharField(verbose_name='Name', max_length=100)),
                ('type', models.CharField(verbose_name='Type', max_length=1, choices=[('F', 'Feeder'), ('U', 'Upriser')])),
                ('voltage', models.PositiveSmallIntegerField(verbose_name='Voltage', choices=[(3, '33KV'), (4, '11KV'), (5, '0.415KV')])),
                ('is_dedicated', models.BooleanField(verbose_name='Dedicated', default=False)),
                ('date_commissioned', models.DateField(verbose_name='Date Commissioned', null=True, blank=True)),
                ('notes', models.TextField(verbose_name='Notes', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('is_active', models.BooleanField(verbose_name='Active', db_index=True, default=True)),
                ('date_created', models.DateTimeField(verbose_name='Date Created', auto_now_add=True)),
                ('last_updated', models.DateTimeField(verbose_name='Last Updated', null=True, auto_now=True)),
                ('code', models.CharField(verbose_name='Code', max_length=10, unique=True)),
                ('name', models.CharField(verbose_name='Name', max_length=100)),
                ('type', models.CharField(verbose_name='Type', max_length=1, choices=[('T', 'Transmission'), ('I', 'Injection'), ('D', 'Distribution')])),
                ('is_dedicated', models.BooleanField(verbose_name='Dedicated', default=False)),
                ('voltage_ratio', models.PositiveSmallIntegerField(verbose_name='Voltage Ratio', choices=[(1, '330/132KV'), (2, '132/33KV'), (4, '33/11KV'), (5, '33/0.415KV'), (6, '11/0.415KV')])),
                ('address_line1', models.CharField(verbose_name='Address Line #1', max_length=50)),
                ('address_line2', models.CharField(verbose_name='Address Line #2', blank=True, max_length=50)),
                ('city', models.CharField(verbose_name='City', max_length=25)),
                ('state', models.CharField(verbose_name='State', max_length=2, choices=[('BE', 'Benue'), ('KO', 'Kogi'), ('KW', 'Kwara'), ('NA', 'Nassarawa'), ('NI', 'Niger'), ('PL', 'Plateau'), ('FC', 'FCT'), ('AD', 'Adamawa'), ('BA', 'Bauchi'), ('BO', 'Borno'), ('GO', 'Gombe'), ('TA', 'Taraba'), ('YO', 'Yobe'), ('JI', 'Jigawa'), ('KD', 'Kaduna'), ('KN', 'Kano'), ('KT', 'Katsina'), ('KE', 'Kebbi'), ('SO', 'Sokoto'), ('ZA', 'Zamfara'), ('AB', 'Abia'), ('AN', 'Anambra'), ('EB', 'Eboyin'), ('EN', 'Enugu'), ('IM', 'Imo'), ('EK', 'Ekiti'), ('LA', 'Lagos'), ('OG', 'Ogun'), ('ON', 'Ondo'), ('OS', 'Osun'), ('OY', 'Oyo'), ('AK', 'Akwa Ibom'), ('BY', 'Bayelsa'), ('CR', 'Cross River'), ('DE', 'Delta'), ('ED', 'Edo'), ('RI', 'Rivers')])),
                ('date_commissioned', models.DateField(verbose_name='Date Commissioned', null=True, blank=True)),
                ('notes', models.TextField(verbose_name='Notes', blank=True)),
                ('source_feeder', models.ForeignKey(null=True, to='network.PowerLine', default=None, verbose_name='Source Feeder', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='powerline',
            name='source_station',
            field=models.ForeignKey(to='network.Station', verbose_name='Source Station', on_delete=django.db.models.deletion.PROTECT, to_field='code'),
        ),
        migrations.AlterUniqueTogether(
            name='powerline',
            unique_together=set([('name', 'voltage')]),
        ),
    ]
