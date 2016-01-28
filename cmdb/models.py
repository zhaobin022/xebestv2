
from django.db import models

# Create your models here.

class App(models.Model):
    app_name =  models.CharField(max_length=30,unique=True)
    upload_path = models.CharField(max_length=100)
    app_path = models.CharField(max_length=100,default='release')
    backup_path =  models.CharField(max_length=100)
    start_script_path =  models.CharField(max_length=100,default='/xebest/tomcat/bin/startup.sh')
    stop_script_path =  models.CharField(max_length=100,default='killall -9 java')
    publish_date = models.DateTimeField(null=True,blank=True)
    war_file = models.NullBooleanField()
    war_file_path = models.CharField(max_length=100,null=True,blank=True)
    task =  models.ForeignKey('TaskLog',null=True,blank=True)
    rollback_status = models.CharField(max_length=30,null=True,blank=True)
    def __unicode__(self):
        return self.app_name

class ServerGroup(models.Model):
    group_name =  models.CharField(max_length=30,unique=True)
    servers  =  models.ManyToManyField('Server',null=True,blank=True)
    description = models.TextField()
    def __unicode__(self):
        return self.group_name
class OsUser(models.Model):
    username =  models.CharField(max_length=30,unique=True)
    server_group = models.ManyToManyField(ServerGroup)

class Server(models.Model):
    server_name = models.CharField(max_length=30,unique=True)
    ipaddr = models.GenericIPAddressField(null=True,unique=True)
    port =  models.IntegerField(blank=True,null=True,default='22310')
    username = models.CharField(max_length=30,null=True,default='root')
    password = models.CharField(max_length=40,null=True)
    new_password = models.CharField(max_length=40,null=True,blank=True)
    app = models.ForeignKey(App,null=True)
    app_status = models.BooleanField(default=True)
    publish_date = models.DateTimeField(blank=True,null=True)
    rollbackup_status = models.CharField(max_length=30,null=True,blank=True)
    task =  models.ForeignKey('TaskLog',null=True,blank=True)
    ssh_check_status = (
        (0, 'Successfull'),
        (1, 'Failed'),
    )
    ssh_check =  models.IntegerField(choices=ssh_check_status,blank=True,null=True,default=1)
    change_password_status = (
        (0, 'Successfull'),
        (1, 'Failed'),
    )
    change_password_tag = models.IntegerField(choices=change_password_status,blank=True,null=True,default=1)
    change_password_time =  models.DateTimeField(blank=True,null=True)
    def __unicode__(self):
        return self.server_name

class Backup(models.Model):

    backup_name = models.CharField(max_length=30)
    app = models.ForeignKey(App,null=True)
    backup_time = models.DateTimeField(auto_now_add=True)

    backup_status = (
        (0, 'Successfull'),
        (1, 'Failed'),
    )
    status =  models.IntegerField(choices=backup_status,blank=True,null=True)

    def __unicode__(self):
        return self.backup_name

class Logger(models.Model):
    happened_time = models.DateTimeField(auto_now_add=True)
    operation_list = (
        (0, 'Publish'),
        (1, 'Backup'),
        (2, 'Rollback'),
        (3, 'Startup'),
        (4, 'Shutdown'),
        (5, 'DeleteBackup'),
        (6, 'UnzipWar'),
        (7, 'CheckApp'),
    )
    operation = models.IntegerField(choices=operation_list)
    server = models.ForeignKey(Server,null=True)
    username = models.CharField(max_length=30)
    operation_status = (
        (0, 'Successfull'),
        (1, 'Failed'),
    )
    status =  models.IntegerField(choices=operation_status,blank=True,null=True)
    description = models.TextField()
    task =  models.ForeignKey('TaskLog',null=True)
    def __unicode__(self):
        return Logger.operation_list[self.operation][1]

class TaskLog(models.Model):
    task_type_list = (
        (0, 'Publish'),
        (1, 'Backup'),
        (2, 'Rollback'),
        (3, 'Startup'),
        (4, 'Shutdown'),
        (5, 'DeleteBackup'),
        (6, 'UnzipWar'),
        (7, 'CheckApp'),
    )
    task_type = models.IntegerField(choices=task_type_list,null=True)
    total_count = models.IntegerField(default=0)
    complete_count = models.IntegerField(default=0)
    def __unicode__(self):
        return str(self.id)