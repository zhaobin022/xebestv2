# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0009_auto_20160118_1337'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasklog',
            name='action_type',
            field=models.IntegerField(null=True, choices=[(0, b'Publish'), (1, b'Backup'), (2, b'Rollback'), (3, b'Startup'), (4, b'Shutdown'), (5, b'DeleteBackup'), (6, b'UnzipWar'), (7, b'CheckApp')]),
        ),
    ]
