# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0016_auto_20160126_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='new_password',
            field=models.CharField(max_length=40, null=True),
        ),
    ]
