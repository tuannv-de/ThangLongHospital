# Generated by Django 5.1.1 on 2024-09-21 21:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointment', '0005_alter_appointment_id'),
        ('doctor_functions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='status',
            field=models.CharField(choices=[('pending', 'Đang chờ'), ('accepted', 'Chấp nhận'), ('completed', 'Đã khám')], default='pending', max_length=10),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='doctor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='doctor_functions.userprofilemodel'),
        ),
    ]
