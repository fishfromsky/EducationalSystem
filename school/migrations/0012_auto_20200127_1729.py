# Generated by Django 2.2.7 on 2020-01-27 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0011_present_semester_cjxq'),
    ]

    operations = [
        migrations.RenameField(
            model_name='present_semester',
            old_name='cjxq',
            new_name='cjxq_ks',
        ),
        migrations.AddField(
            model_name='present_semester',
            name='cjxq_ps',
            field=models.CharField(default='0', max_length=5),
        ),
    ]
