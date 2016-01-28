# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0011_auto_20160120_1002'),
    ]

    operations = [
        migrations.AddField(
            model_name='app',
            name='rollbackup_status',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
    ]
