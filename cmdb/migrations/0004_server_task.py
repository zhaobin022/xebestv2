# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0003_auto_20160113_1753'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='task',
            field=models.ForeignKey(to='cmdb.TaskLog', null=True),
        ),
    ]
