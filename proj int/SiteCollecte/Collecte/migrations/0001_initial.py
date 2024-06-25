# Generated by Django 5.0.4 on 2024-06-25 11:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('sensor_id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, null=True)),
                ('emplacement', models.CharField(blank=True, max_length=255, null=True)),
                ('piece', models.CharField(max_length=255, null=True)),
            ],
            options={
                'db_table': 'sensor',
            },
        ),
        migrations.CreateModel(
            name='TemperatureData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('value', models.DecimalField(decimal_places=2, max_digits=5)),
                ('sensor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Collecte.sensor')),
            ],
            options={
                'db_table': 'temperaturedata',
            },
        ),
    ]
