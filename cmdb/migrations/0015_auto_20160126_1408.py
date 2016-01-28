# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0014_server_ssh_check'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='ssh_check',
            field=models.IntegerField(default=1, null=True, blank=True, choices=[(0, b'Successfull'), (1, b'Failed')]),
        ),
    ]
