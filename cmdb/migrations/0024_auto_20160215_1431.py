# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0023_auto_20160128_1730'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='server_name',
            field=models.CharField(unique=True, max_length=30, verbose_name='\u670d\u52a1\u5668\u540d'),
        ),
    ]
