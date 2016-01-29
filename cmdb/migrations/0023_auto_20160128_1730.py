# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0022_auto_20160128_1648'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servergroup',
            name='servers',
            field=models.ManyToManyField(to='cmdb.Server'),
        ),
    ]
