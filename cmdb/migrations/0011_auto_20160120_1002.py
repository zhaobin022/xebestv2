# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0010_tasklog_action_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tasklog',
            old_name='action_type',
            new_name='task_type',
        ),
    ]
