# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0021_auto_20160128_1641'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='server',
            name='server_group',
        ),
        migrations.AddField(
            model_name='servergroup',
            name='servers',
            field=models.ManyToManyField(to='cmdb.Server', null=True, blank=True),
        ),
    ]
