# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0024_auto_20160215_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='app',
            field=models.ForeignKey(blank=True, to='cmdb.App', null=True),
        ),
    ]
