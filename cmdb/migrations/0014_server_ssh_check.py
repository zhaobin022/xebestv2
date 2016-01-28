# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0013_auto_20160121_1111'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='ssh_check',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Successfull'), (1, b'Failed')]),
        ),
    ]
