from cmdb import models
from xebest import settings
from multiprocessing import Pool
import multiprocessing
import commands
import django.utils.timezone
from utils.tools import rsyncCode
from utils.tools import execute_cmd
from django.http import HttpResponse, HttpResponseRedirect
from utils.tools import str_to_html
from utils.tools import backup_code
from utils.tools import rollback_code
import shutil
from utils.tools import empty_dir
import os
import logging
logger = logging.getLogger('web_apps')

def publish_all(request):
    try:
        if request.method == 'POST':
            task_id = request.POST.get('task_id')
            task = models.TaskLog.objects.get(id=task_id)
            username = request.user.username
            app_id = request.POST.get('app_id')
            app = models.App.objects.get(id = app_id)
            server_list = models.Server.objects.filter(app = app)

            publishTime = django.utils.timezone.now()
            #currentVersion = publishTime.strftime("%Y%m%d%H%M%S")
            #currentVersion = (publishTime + django.utils.timezone.timedelta(hours=8)).strftime("%Y%m%d%H%M%S")
            app.publish_date = publishTime
            app.task = task
            app.save()


            unzip_status = 1
            task.total_count = server_list.count()
            if app.war_file:
                task.total_count += 1
                task.save()
                unzip_cmd = '/usr/bin/unzip -o %s -d %s' %(app.war_file_path,app.upload_path)
                unzip_status , result = commands.getstatusoutput(unzip_cmd)
                logger.info('unzip file : status : %s , resutls : %s' % (unzip_status,result))

                if unzip_status == 0:
                    models.Logger.objects.create(status=unzip_status,username=username,description=result,operation=6,task=task)
                else:
                    models.Logger.objects.create(status=1,username=username,description=result,operation=6,task=task)
                    return False,''


            p = Pool(multiprocessing.cpu_count())
            for s in server_list:
                status = p.apply_async(rsyncCode, args=(s,app,username,unzip_status,task)).get()
                if status == 0:
                    s.publish_date = publishTime
                   # s.rollbackup_status = currentVersion
                    s.save()
            p.close()
            p.join()
            if app.war_file:
                empty_dir(app.upload_path)
            return True,task.id
    except Exception,e:
        return False,str(e)


def get_execute_result(request):
    if request.method == "POST":
        try:
            result_list  = []
            task_id = request.POST.get('task_id')
            task = models.TaskLog.objects.get(id=task_id)
            app_list = task.app_set.filter()
            app_id = app_list[0].id
            app = models.App.objects.get(id=app_id)
            logger_list = task.logger_set.all()
            if task.task_type == 2:
                total_count = models.Server.objects.filter(app=app).count()
                #successfull_count = models.Server.objects.filter(rollbackup_status=app.rollback_status).count()
                #successfull_count = models.Server.objects.filter(task_id=task.id).count()
                successfull_count = models.Logger.objects.filter(task=task,status=0).count()
                failed_count = total_count - successfull_count
            else:
                total_count = task.total_count
                successfull_count = models.Logger.objects.filter(task=task,status=0).count()
                failed_count = total_count - successfull_count
            count = 0
            for i in logger_list:
                result = i.description[0:500]
                result = str_to_html(result)
                if i.operation == 6 :
                    result_dic = {
                            'war_file':True,
                            'operation_type' :  i.get_operation_display(),
                            'status' : i.get_status_display(),
                            'result' : result,
                    }
                else:
                    result_dic = {
                            'war_file':False,
                            'server_name' : i.server.server_name,
                            'ipaddr' : i.server.ipaddr,
                            'operation_type' :  i.get_operation_display(),
                            'status' : i.get_status_display(),
                            'result' : result,
                    }
                if count==0:
                    result_dic['rollback_status'] = app.rollback_status
                    result_dic['total_count'] = total_count
                    result_dic['successfull_count'] = successfull_count
                    result_dic['failed_count'] = failed_count


                result_list.append(result_dic)
                count+=1
            return result_list
        except Exception,e:
            logger.info(str(e))



def get_server_list(request):
    if request.method == 'POST':
        app_id = request.POST.get('app_id')
        server_list = models.Server.objects.filter(app__id = app_id)
        result_list = []
        for i in server_list:
            result_dic = {}
            result_dic['id'] = i.id
            result_dic['server_name'] = i.server_name
            result_dic['ipaddr'] = i.ipaddr
            result_dic['app_status'] = i.app_status
#            result_dic['publish_date'] = i.publish_date+django.utils.timezone.timedelta(hours=8)
            result_dic['publish_date'] = i.publish_date
            result_dic['rollbackup_status'] = i.rollbackup_status
            result_dic['task_id'] = i.task_id
            result_list.append(result_dic)

        return result_list


def get_process_status(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        app = models.App.objects.get(task_id = task_id)
        task = models.TaskLog.objects.get(id = task_id )
        try:
            logger = models.Logger.objects.filter(task = task)[0]
        except Exception,e:
            return False,'sleep'
        total_count = task.total_count

        complete_count = models.Logger.objects.filter(task_id = task_id).count()
        percent = int(float(complete_count)/float(total_count)*100)
        return True,percent



def startup_all(request):
    try:
        if request.method == 'POST':
            task_id = request.POST.get('task_id')
            task = models.TaskLog.objects.get(id=task_id)
            username = request.user.username
            app_id = request.POST.get('app_id')
            app = models.App.objects.get(id = app_id)
            app.task_id = task.id
            app.save()
            server_list = models.Server.objects.filter(app  = app)
            cmd = app.start_script_path
            cmd += ' && echo 0 || echo 1'
            p = Pool(multiprocessing.cpu_count())

             #   publishTime = timezone.now()
              #  app.publish_date = publishTime
               # app.save()
            result_list = []
            for s in server_list:
                if s.app_status:
                    models.Logger.objects.create(
                        status=1,
                        username=username,
                        description='''The Tomcat is already startup !  Don't startup again ! ''',
                        operation=3,
                        server=s,
                        task=task
                    )
                    s.task = task
                    s.save()
                    continue
                result = p.apply_async(execute_cmd, args=(s,cmd)).get()
                logger.info('startup all result : %s' % ' '.join(result) )
                if len(result) != 0:
                    if len(result) == 1:
                        status = result[0].strip()
                        if status == '0':
                            s.app_status = 1
                            models.Logger.objects.create(status=status,username=username,description="startup successfull !",operation=3,server=s,task=task)
                            s.task = task
                            s.app_status = True
                        elif status == '1':
                            s.task = task
                            s.app_status = 0
                            models.Logger.objects.create(status=1,username=username,description="startup failed !",operation=3,server=s,task=task)
                        s.save()
                    elif len(result) == 2:
                        status = result[1].strip()

                        if status == '0':
                            s.app_status = 1
                            models.Logger.objects.create(status=status,username=username,description=result[0],operation=3,server=s,task=task)
                            s.task = task
                            s.app_status = True
                        elif status == '1':
                            s.task = task
                            s.app_status = 0
                            models.Logger.objects.create(status=1,username=username,description=result[0],operation=3,server=s,task=task)
                        s.save()
            p.close()
            p.join()
            return True,task.id
    except Exception,e:
        logger.info('startup all execption msg : %s' % str(e))
        return False,str(e)


def gen_task_log(request):
    if request.method == 'POST':
        task = models.TaskLog.objects.create()
        server_ids = request.POST.getlist('server_ids[]')
        app_id = request.POST.get('app_id')
        task_type = request.POST.get('task_type')
        task_type = int(task_type)


        task.task_type = task_type
        app = models.App.objects.get(id=app_id)
        app.task = task
        app.save()
        selected = request.POST.get('selected')
        if selected.strip() == 'true':
            if  server_ids:
                task.total_count += len(server_ids)
                if task.task_type == 0 and app.war_file:task.total_count +=1
                task.save()
                return True,task.id
            else:
                return False,None

        elif selected.strip() == 'false':
            task.total_count = app.server_set.all().count()

        if task.task_type == 1:
            task.total_count=1;
            task.save()
            return  True,task.id
        elif task.task_type == 2 or task.task_type == 7 or task.task_type == 3 or task.task_type == 4:
            task.total_count = app.server_set.all().count()
            task.save()
            return  True,task.id




        if app.war_file:
            task.total_count += 1
        task.save()
        return  True,task.id


def check_all(request):
    if request.method == 'POST':
        app_id = request.POST.get('app_id')
        app = models.App.objects.get(id = app_id)
        task_id = request.POST.get('task_id')
        task = models.TaskLog.objects.get(id=task_id)
        app.task = task
        app.save()
        server_list = models.Server.objects.filter(app  = app)
        cmd = 'ps -ef | grep java | grep -v grep'
        username = request.user.username
        p = Pool(multiprocessing.cpu_count())
        for s in server_list:
            result = p.apply_async(execute_cmd, args=(s,cmd,)).get()
            if len(result) != 0:
                s.app_status = 1
                s.task = task
                s.save()
                models.Logger.objects.create(status=0,username=username,description=('\n').join(result),operation=7,server=s,task=task)

            else:
                s.app_status = 0
                s.task = task
                s.save()
                models.Logger.objects.create(status=1,username=username,description='The tomcat is not running !',operation=7,server=s,task=task)



        p.close()
        p.join()
        return True,''

def shutdown_all(request):
    if request.method == "POST":
        app_id = request.POST.get('app_id')
        app = models.App.objects.get(id = app_id)
        task_id = request.POST.get('task_id')
        task = models.TaskLog.objects.get(id=task_id)
        app.task = task
        app.save()
        username = request.user.username
        server_list = models.Server.objects.filter(app  = app)
        cmd = app.stop_script_path
        cmd += ' && echo 0 || echo 1'
        p = Pool(multiprocessing.cpu_count())
        for s in server_list:
            if not s.app_status:
                s.task
                s.save()
                models.Logger.objects.create(status=1,username=username,description='''Can't shutdown the offline server  !''',operation=4,server=s,task=task)
                continue
            result = p.apply_async(execute_cmd, args=(s,cmd,)).get()
            if len(result) != 0:
                status = result[0].strip()
                if status == '1':
                    s.app_status = True
                    s.task = task
                    s.save()
                    models.Logger.objects.create(status=1,username=username,description='Shutdown Error !',operation=4,server=s,task=task)
                elif status == '0':
                    s.app_status = False
                    s.task = s.task
                    s.save()
                    models.Logger.objects.create(status=0,username=username,description='Shutdown Successfull !',operation=4,server=s,task=task)
        p.close()
        p.join()
        return True,''


def publish_selected(request):
    if request.method == "POST":
        try:
            task_id = request.POST.get('task_id')
            task = models.TaskLog.objects.get(id=task_id)
            username = request.user.username
            app_id = request.POST.get('app_id')
            app = models.App.objects.get(id = app_id)
            server_ids = request.POST.getlist('server_ids[]')
            server_list = models.Server.objects.filter(id__in   = server_ids)
            publishTime = django.utils.timezone.now()
            #currentVersion = publishTime.strftime("%Y%m%d%H%M%S")
            #currentVersion = (publishTime + django.utils.timezone.timedelta(hours=8)).strftime("%Y%m%d%H%M%S")
            app.publish_date = publishTime
            app.task = task
            app.save()


            unzip_status = 1
            if app.war_file:
                unzip_cmd = '/usr/bin/unzip -o %s -d %s' %(app.war_file_path,app.upload_path)
                unzip_status , result = commands.getstatusoutput(unzip_cmd)
                logger.info('publish selected unzip status : %s , result : %s ' % (unzip_status,result))
                if unzip_status == 0:
                    models.Logger.objects.create(status=unzip_status,username=username,description=result,operation=6,task=task)
                else:
                    models.Logger.objects.create(status=1,username=username,description=result,operation=6,task=task)
                    return
            p = Pool(multiprocessing.cpu_count())
            for s in server_list:
                status = p.apply_async(rsyncCode, args=(s,app,username,unzip_status,task)).get()
                if status == 0:
                    s.publish_date = publishTime
                   # s.rollbackup_status = currentVersion
                    s.save()
            p.close()
            p.join()
            if app.war_file:
                empty_dir(app.upload_path)
            return True,task.id
        except Exception,e:
            logger.info(str(e))
            return False,str(e)



def startup_selected(request):
    try:
        if request.method == 'POST':
            task_id = request.POST.get('task_id')
            task = models.TaskLog.objects.get(id=task_id)
            username = request.user.username
            app_id = request.POST.get('app_id')
            app = models.App.objects.get(id = app_id)
            app.task_id = task.id
            app.save()
            server_ids = request.POST.getlist('server_ids[]')
            server_list = models.Server.objects.filter(id__in  = server_ids)
            cmd = app.start_script_path
            cmd += ' && echo 0 || echo 1'
            p = Pool(multiprocessing.cpu_count())

             #   publishTime = timezone.now()
              #  app.publish_date = publishTime
               # app.save()
            result_list = []
            for s in server_list:
                if s.app_status:
                    models.Logger.objects.create(
                        status=1,
                        username=username,
                        description='''The Tomcat is already startup !  Don't startup again ! ''',
                        operation=3,
                        server=s,
                        task=task
                    )
                    s.task = task
                    s.save()
                    continue
                result = p.apply_async(execute_cmd, args=(s,cmd)).get()


                if len(result) != 0:
                    status = result[1].strip()
                    if status == '0':
                        s.app_status = 0
                        models.Logger.objects.create(status=status,username=username,description=result,operation=3,server=s,task=task)
                        s.task = task
                        s.app_status = True
                    elif status == '1':
                        s.task = task
                        s.app_status = 1
                        models.Logger.objects.create(status=1,username=username,description=result,operation=3,server=s,task=task)
                    s.save()
            p.close()
            p.join()
            return True,task.id
    except Exception,e:
        return False,str(e)


def shutdown_selected(request):
    if request.method == "POST":
        app_id = request.POST.get('app_id')
        app = models.App.objects.get(id = app_id)
        task_id = request.POST.get('task_id')
        task = models.TaskLog.objects.get(id=task_id)
        app.task = task
        app.save()
        username = request.user.username
        server_ids = request.POST.getlist('server_ids[]')
        server_list = models.Server.objects.filter(id__in  = server_ids)
        cmd = app.stop_script_path
        cmd += ' && echo 0 || echo 1'
        p = Pool(multiprocessing.cpu_count())
        for s in server_list:
            if not s.app_status:
                s.task
                s.save()
                models.Logger.objects.create(status=1,username=username,description='''Can't shutdown the offline server  !''',operation=4,server=s,task=task)
                continue
            result = p.apply_async(execute_cmd, args=(s,cmd,)).get()
            if len(result) != 0:
                status = result[0].strip()
                if status == '1':
                    s.app_status = True
                    s.task = task
                    s.save()
                    models.Logger.objects.create(status=1,username=username,description='Shutdown Error !',operation=4,server=s,task=task)
                elif status == '0':
                    s.app_status = False
                    s.task = task
                    s.save()
                    models.Logger.objects.create(status=0,username=username,description='Shutdown Successfull !',operation=4,server=s,task=task)


        p.close()
        p.join()
        return True,''


def create_backup(request):
    if request.method == 'POST':
         app_id = request.POST.get('app_id')
         task_id = request.POST.get('task_id')
         task = models.TaskLog.objects.get(id = task_id)
         username = request.user.username
         app = models.App.objects.get(id=app_id)
         server = models.Server.objects.filter(app = app).first()
         if server == None:
             return True,''
         backup_code(server,app,username,task)
         return True,''

def get_backup_list(request):
    if request.method == 'POST':
        app_id = request.POST.get('app_id')
        backup_list = models.Backup.objects.filter(app__id = app_id).order_by('-backup_time')[:10]
        result_list = []
        for i in backup_list:
            result_dic = {}
            result_dic['id'] = i.id
            result_dic['backup_name'] = i.backup_name
            result_dic['backup_time'] = i.backup_time
            result_dic['status'] = i.get_status_display()
            result_list.append(result_dic)

        return result_list

def rollback(request):
    if request.method == "POST":
        app_id = request.POST.get('app_id')
        backup_id = request.POST.get('backup_id')
        task_id = request.POST.get('task_id')
        app = models.App.objects.get(id=app_id)
        backup = models.Backup.objects.get(id=backup_id)
        task = models.TaskLog.objects.get(id=task_id)
        username = request.user.username
        rollback_code(app,backup,username,task)
        return True,'finish'