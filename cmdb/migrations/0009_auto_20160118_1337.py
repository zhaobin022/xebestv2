# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0008_auto_20160115_1513'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasklog',
            name='complete_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tasklog',
            name='total_count',
            field=models.IntegerField(default=0),
        ),
    ]
