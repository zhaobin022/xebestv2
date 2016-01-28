# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0020_osuser'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='server',
            name='server_group',
        ),
        migrations.AddField(
            model_name='server',
            name='server_group',
            field=models.ManyToManyField(to='cmdb.ServerGroup', null=True, blank=True),
        ),
    ]
