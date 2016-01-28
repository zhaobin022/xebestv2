# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0005_app_task'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='task',
            field=models.ForeignKey(blank=True, to='cmdb.TaskLog', null=True),
        ),
    ]
