# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='App',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('app_name', models.CharField(unique=True, max_length=30)),
                ('upload_path', models.CharField(max_length=100)),
                ('app_path', models.CharField(default=b'release', max_length=100)),
                ('backup_path', models.CharField(max_length=100)),
                ('start_script_path', models.CharField(default=b'/xebest/tomcat/bin/startup.sh', max_length=100)),
                ('stop_script_path', models.CharField(default=b'killall -9 java', max_length=100)),
                ('publish_date', models.DateTimeField(null=True, blank=True)),
                ('war_file', models.NullBooleanField()),
                ('war_file_path', models.CharField(max_length=100, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Backup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('backup_name', models.CharField(max_length=30)),
                ('backup_time', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(blank=True, null=True, choices=[(0, b'Successfull'), (1, b'Failed')])),
                ('app', models.ForeignKey(to='cmdb.App', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Logger',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('happened_time', models.DateTimeField(auto_now_add=True)),
                ('operation', models.IntegerField(choices=[(0, b'Publish'), (1, b'Backup'), (2, b'Rollback'), (3, b'Startup'), (4, b'Shutdown'), (5, b'DeleteBackup'), (6, b'UnzipWar')])),
                ('username', models.CharField(max_length=30)),
                ('status', models.IntegerField(blank=True, null=True, choices=[(0, b'Successfull'), (1, b'Failed')])),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('server_name', models.CharField(unique=True, max_length=30)),
                ('ipaddr', models.GenericIPAddressField(unique=True, null=True)),
                ('port', models.IntegerField(default=b'22310', null=True, blank=True)),
                ('username', models.CharField(default=b'root', max_length=30, null=True)),
                ('password', models.CharField(max_length=40, null=True)),
                ('app_status', models.IntegerField(blank=True, null=True, choices=[(0, b'Online'), (1, b'Offline')])),
                ('publish_date', models.DateTimeField(null=True, blank=True)),
                ('rollbackup_status', models.CharField(max_length=30, null=True, blank=True)),
                ('app', models.ForeignKey(to='cmdb.App', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='logger',
            name='server',
            field=models.ForeignKey(to='cmdb.Server', null=True),
        ),
    ]
