# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0012_app_rollbackup_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='app',
            old_name='rollbackup_status',
            new_name='rollback_status',
        ),
    ]
