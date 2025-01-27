# Generated by Django 3.2.23 on 2024-10-17 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FuelStop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opis_truckstop_id', models.CharField(max_length=100)),
                ('truckstop_name', models.CharField(max_length=255)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, max_length=50, null=True)),
                ('rack_id', models.CharField(blank=True, max_length=50, null=True)),
                ('retail_price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
        ),
    ]
