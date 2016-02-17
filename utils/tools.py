__author__ = 'zhaobin022'
#!/usr/bin/env python
# coding=utf-8
import commands
from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger
import paramiko
from cmdb import models
from conf import global_setttings
import django.utils.timezone
import multiprocessing
from multiprocessing import Pool
import os
import shutil
import logging
logger = logging.getLogger('web_apps')


import time
def json_date_handler(obj):
    if hasattr(obj, 'isoformat'):
        obj = obj + django.utils.timezone.timedelta(hours=8)
        return obj.strftime("%Y-%m-%d %T")
    #elif isinstance(obj, ...):
    #    return obj
    #else:
    #    raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))

def json_date_to_stamp(obj):
    if hasattr(obj, 'isoformat'):
        return time.mktime(obj.timetuple()) *1000


def str_to_html(s):
    s = s.replace('\n','</br>').replace(' ','&nbsp;')
    return s

def pagetool(page,obj_list,page_size=3,after_range_num=3, before_range_num=3):
    page_objects = ''
    try:
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    paginator = Paginator(obj_list,page_size)
    try:
        page_objects = paginator.page(page)
    except(EmptyPage,InvalidPage,PageNotAnInteger):
        page_objects = paginator.page(1)
        page = 1
    if page >= after_range_num:
        page_range = paginator.page_range[page-after_range_num:page+before_range_num]
    else:
        page_range = paginator.page_range[0:int(page)+before_range_num]
    return page_range,page_objects


def execute_cmd(s,cmd):
    try:

        logger.info('server %s execute cmd %s' % (s.ipaddr,cmd))
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(s.ipaddr,s.port,s.username, s.password)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.readlines()
        ssh.close()
    except Exception , e:
        logger.info(str(e))
        return ['1',str(e)]
    return result

def rsyncCode(s,app,username,unzip_status,task):
    try:
        cmd=''
        upload_path = app.upload_path
        if not app.upload_path.endswith("/"):
            upload_path+="/"
        app_path = app.app_path
        if not app.app_path.endswith("/"):
            app_path+="/"
        app_name = app.app_name
        if not app.app_path.endswith("/"):
            app_name+="/"
        if app.war_file:
    #        unzip_cmd = '/usr/bin/unzip -o %s -d %s' %(app.war_file_path,app.upload_path)
    #        unzip_status , result = commands.getstatusoutput(unzip_cmd)
            if unzip_status == 0:
                cmd = '/usr/bin/rsync -av --delete --password-file=%s  %s %s@%s::%s/%s' % (
                    global_setttings.rsync_server_dic['secure_file_path'],
                    upload_path,
                    global_setttings.rsync_server_dic['rsync_login_user'],
                    s.ipaddr,
                    global_setttings.rsync_server_dic['warehouse'],
                    app_path
                )
            else:
                cmd = '/usr/bin/rsync -av --password-file=%s  %s %s@%s::%s/%s' % (
                    global_setttings.rsync_server_dic['secure_file_path'],
                    upload_path,
                    global_setttings.rsync_server_dic['rsync_login_user'],
                    s.ipaddr,
                    global_setttings.rsync_server_dic['warehouse'],
                    app_path
                )


        else:
            cmd = '/usr/bin/rsync -av --password-file=%s  %s %s@%s::%s/%s' % (
                global_setttings.rsync_server_dic['secure_file_path'],
                upload_path,
                global_setttings.rsync_server_dic['rsync_login_user'],
                s.ipaddr,
                global_setttings.rsync_server_dic['warehouse'],
                app_path
            )
        logger.info(cmd)
        status,result = commands.getstatusoutput(cmd)
        logger.info(status)
        logger.info(result)
        if status == 0:
            s.task = task;
            s.publish_date = app.publish_date
            models.Logger.objects.create(status=status,username=username,description=result,operation=0,server=s,task=task)
        else:
            models.Logger.objects.create(status=1,username=username,description=result,operation=0,server=s,task=task)
            s.task = task;
        s.save()
    except Exception,e:
        print e



def backup_code(s,app,username,task):
    backupTime = django.utils.timezone.now()
    backupName = (backupTime + django.utils.timezone.timedelta(hours=8)).strftime("%Y%m%d%H%M%S")

 #   backupName = backupTime.strftime("%Y%m%d%H%M%S")
    app_path = app.app_path
    if not app_path.endswith('/'):
        app_path += '/'
    backup_path = app.backup_path
    if not backup_path.endswith('/'):
        backup_path+= '/'

    cmd = '/usr/bin/rsync -av --password-file=%s  %s@%s::%s/%s %s%s' % (
                                                        global_setttings.rsync_server_dic['secure_file_path'],
                                                        global_setttings.rsync_server_dic['rsync_login_user'],
                                                        s.ipaddr,
                                                        global_setttings.rsync_server_dic['warehouse'],
                                                        app_path,
                                                        backup_path,
                                                        backupName)
    logger.info(cmd)
    status,result = commands.getstatusoutput(cmd)
    logger.info(status)
    logger.info(result)
    if status == 0:
        models.Backup.objects.create(backup_name=backupName,app=app,status=status,backup_time=backupTime)
        models.Logger.objects.create(status=0,username=username,description=result,operation=1,server=s,task=task)
    else:
        models.Backup.objects.create(backup_name=backupName,app=app,status=1)
        models.Logger.objects.create(status=1,username=username,description=result,operation=1,server=s,task=task)


    return status


def rollback_code(app,backup,username,task):

    backup_path = app.backup_path
    if not backup_path.endswith("/"):
        backup_path+="/"
    app_path = app.app_path
    if not app.app_path.endswith("/"):
        app_path+="/"
    backup_name = backup.backup_name
    if not backup_name.endswith("/"):
        backup_name+="/"
    app.rollback_status = backup_name.strip('/')
    app.save()
    server_list = models.Server.objects.filter(app = app)
    status = 0
    p = Pool(multiprocessing.cpu_count())
    for s in server_list:
        cmd = '/usr/bin/rsync -av --delete --password-file=%s  %s%s %s@%s::%s/%s' % (
                                                    global_setttings.rsync_server_dic['secure_file_path'],
                                                    backup_path,
                                                    backup_name,
                                                    global_setttings.rsync_server_dic['rsync_login_user'],
                                                    s.ipaddr,
                                                    global_setttings.rsync_server_dic['warehouse'],
                                                    app_path)
        logger.info(cmd)
        result = p.apply_async(commands.getstatusoutput, args=(cmd,)).get()
        logger.info(result[0])
        logger.info(result[1])
        if result[0] == 0:
            s.rollbackup_status = backup_name.strip('/')
            models.Logger.objects.create(status=0,username=username,description=result[1],operation=2,server=s,task=task)
        else:
            models.Logger.objects.create(status=1,username=username,description=result[1],operation=2,server=s,task=task)
        s.task = task
        s.save()
    p.close()
    p.join()


def get_dir_content(dir_path):
    if os.path.isdir(dir_path):
        cmd = '/usr/bin/tree -L 2 %s' % (dir_path)
        status,result = commands.getstatusoutput(cmd)
        if status == 0:
            status = True
        else:
            status = False
        result = str_to_html(result)
    else:
        return False,'dir not exist !'
    return status,result


def empty_dir(dir_path):
    delList = []
    delList = os.listdir(dir_path)

    for f in delList:
        filePath = os.path.join( dir_path, f )
        if os.path.isfile(filePath):
            os.remove(filePath)
            print filePath + " was removed!"
        elif os.path.isdir(filePath):
            shutil.rmtree(filePath,True)
            print "Directory: " + filePath +" was removed!"
