# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0004_server_task'),
    ]

    operations = [
        migrations.AddField(
            model_name='app',
            name='task',
            field=models.ForeignKey(to='cmdb.TaskLog', null=True),
        ),
    ]
