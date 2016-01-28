# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0006_auto_20160115_1135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logger',
            name='operation',
            field=models.IntegerField(choices=[(0, b'Publish'), (1, b'Backup'), (2, b'Rollback'), (3, b'Startup'), (4, b'Shutdown'), (5, b'DeleteBackup'), (6, b'UnzipWar'), (7, b'UnzipWar')]),
        ),
    ]
