from django.shortcuts import render
from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from django.contrib import auth
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json,datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import django.utils.timezone
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response
from cmdb import models
from utils.tools import pagetool
from backend import publish_api
from utils.tools import json_date_handler
import shutil
import os
import re
from django.db.models import Q
from utils.tools import get_dir_content
from utils.tools import str_to_html
import logging
from multiprocessing import Pool
import multiprocessing
from utils.flushpassword import GenPassword
from utils.flushpassword import ssh_cmd
from django.http import HttpResponseRedirect
from utils.tools import execute_cmd
import xlwt
import StringIO

@login_required
def index(request):
    if request.method == "GET":
        page_objects = ''
        app_name = request.GET.get('app_name')
        try:
            page = int(request.GET.get("page",1))
            if page < 1:
                page = 1
        except ValueError:
            page = 1
        if app_name:
            app_list = models.App.objects.filter(app_name__icontains=app_name.strip())
        else:
            app_list = models.App.objects.all()


        page_range,page_objects = pagetool(page,app_list,page_size=10)
        username = request.user
        search = None
        return render(request,'index.html',{'page_objects':page_objects,'page_range':page_range,'username':username,'app_list':app_list,'search':search})


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect('/')
        else:
            return render_to_response('sign-in.html')
    else:
        return render_to_response('sign-in.html')


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/login/')


def server_list(request):
    if request.method == 'GET':
        app_id = request.GET.get('app_id')
        app = models.App.objects.get(id=app_id)
        try:
            page = int(request.GET.get("page",1))
            if page < 1:
                page = 1
        except ValueError:
            page = 1
        server_list = models.Server.objects.filter(app = app)
        page_range,page_objects = pagetool(page,server_list)
        username = request.user
        return render_to_response('server-list.html',{'page_objects':page_objects,'page_range':page_range,'username':username,'app':app})


def publish_api_view(request):
    if request.method == 'POST':
        try:
            action_type = request.POST.get('action_type')
            if hasattr(publish_api,action_type):
                func = getattr(publish_api,action_type)
                results = func(request)
                if results:
                    return HttpResponse(json.dumps(results,default=json_date_handler))
                else:
                    return HttpResponse('finish')
            else:
                return HttpResponse('finish')
        except Exception,e:
            logging.info(str(e))

def backup_list(request):
    if request.method == 'GET':
        app_id = request.GET.get('app_id')
        app = models.App.objects.get(id=app_id)
        try:
            page = int(request.GET.get("page",1))
            if page < 1:
                page = 1
        except ValueError:
            page = 1
        backup_list = models.Backup.objects.filter(app = app).order_by('-backup_time')
        page_range,page_objects = pagetool(page,backup_list,page_size=10)
        username = request.user
        return render_to_response('backup-list.html',{'page_objects':page_objects,'page_range':page_range,'username':username,'app':app})

def delete_backup(request):
    if request.method == 'POST':
        try:
            backup_ids = request.POST.getlist('backup_ids[]')
            app_id = request.POST.get('app_id')
            app = models.App.objects.get(id =app_id )
            backup_list = models.Backup.objects.filter(id__in =backup_ids  )
            pattern = re.compile(r'[\w|/]+\d{14}')
            for b in backup_list:
                delete_path = os.path.join(app.backup_path,b.backup_name)
                match = pattern.match(delete_path)
                if match:
                    if os.path.exists(delete_path):
                        logging.info('delete bakcup id %s path %s' % (b.id,delete_path))
                        shutil.rmtree(delete_path)
                b.delete()
        except Exception,e:
            logging.info(str(e))


        return HttpResponse('finish')

def log_list(request):
    if request.method == 'GET':
        conditions = {}
        con = Q()
        app_id = request.GET.get('app_id')
        key_words = request.GET.get('key_words')
        operation_id = request.GET.get('operation_id')
        if app_id.isdigit():
            con.add(('server__app_id',int(app_id)),'AND')
        if operation_id:
            if operation_id.isdigit():
                operation_id = int(operation_id)
                con.add(('operation',operation_id),'AND')
            else:
                operation_id = ''

        if key_words:
            if key_words != 'None':
                if len(key_words) != 0:
                    conditions['server__server_name__icontains']=key_words
                    conditions['username__icontains']=key_words
            else:
                key_words = ''
        app = models.App.objects.get(id=app_id)
        successful_count = models.Logger.objects.filter(server__app = app,status=0).count()
        failed_count = models.Logger.objects.filter(server__app = app,status=1).count()
        username = request.user.username
        operation_list = models.Logger.operation_list

        temp = Q()
        temp.connector = 'OR'
        for k,v in conditions.items():
            temp.children.append((k,v))

        con.add(temp,'AND')
        log_list = models.Logger.objects.filter(con).order_by('-happened_time')
        total_count = log_list.count()

        try:
            page = int(request.GET.get("page",1))
            if page < 1:
                page = 1
        except ValueError:
            page = 1
        page_range,page_objects = pagetool(page,log_list,page_size=10)

        search = None
        return render_to_response('log-list.html',{
                                                'page_objects':page_objects,
                                                'page_range':page_range,
                                                'username':username,
                                                'app':app,
                                                'operation_list':operation_list,
                                                'total_count':total_count,
                                                'key_words':key_words,
                                                'successful_count':successful_count,
                                                'failed_count':failed_count,
                                                'operation_id':operation_id,
                                    })


def display_dir_content(request):
    if request.method == 'POST':
        try:
            dir_path = request.POST.get('dir_path')
            status , reslts = get_dir_content(dir_path)
        except Exception,e:
            logging.info(str(e))
        return HttpResponse(json.dumps((status,reslts)))


def display_log_detail(request):
    if request.method == 'POST':
        log_id = request.POST.get('log_id')
        log = models.Logger.objects.get(id=log_id)
        return HttpResponse(json.dumps((True,str_to_html(log.description))))



def cmdb_main(request):
    try:
        if request.method == 'GET':

            page_objects = ''
            try:
                page = int(request.GET.get("page",1))
                if page < 1:
                    page = 1
            except ValueError:
                page = 1
            cmdb_server_list = models.Server.objects.all()
            group_name = request.GET.get('group_name')
            server_name = request.GET.get('server_name')
            if group_name:
                if len(group_name) != 0:
                    #cmdb_server_list = cmdb_server_list.filter(server_group__group_name = group_name.strip() )
                    cmdb_server_list = models.ServerGroup.objects.get(group_name=group_name).servers.all()
            if server_name:
                if len(server_name) != 0:
                    cmdb_server_list = cmdb_server_list.filter(server_name__istartswith = server_name.strip() )


            page_range,page_objects = pagetool(page,cmdb_server_list,page_size=50)
            username = request.user
            group_list = models.ServerGroup.objects.values('group_name').distinct()
            group_name_list = []
            for i in group_list:
                group_name_list.append(i['group_name'])

            if not server_name:server_name = ''
            if not group_name:group_name = ''
            return render(request,'main_cmdb.html',{
                'page_objects':page_objects,
                'page_range':page_range,
                'username':username,
                'server_list':cmdb_server_list,
                'server_name':server_name,
                'group_name':group_name,
                'group_name_list' : group_name_list,
            })

        elif request.method == 'POST':
            try:
                page = int(request.POST.get("page",1))
                if page < 1:
                    page = 1
            except ValueError:
                page = 1
            group_name = request.POST.get('group_name')
            server_name = request.POST.get('server_name')
            action_type = request.POST.get('action_type')
            if action_type:
                if len(action_type) != 0:
                    if action_type.strip() == 'gen_password':
                        cmdb_server_list = models.Server.objects.all()
                        for s in cmdb_server_list:
                            newpassword = GenPassword()
                            s.new_password = newpassword
                            s.save()
                    elif action_type.strip() == 'reset_password':
                        server_ids = request.POST.getlist('checkbox_list')
                        cmdb_server_list = models.Server.objects.filter(id__in = server_ids)
                        p = Pool(multiprocessing.cpu_count())
                        for s in cmdb_server_list:
                            status = p.apply_async(ssh_cmd, args=(s,s.new_password,)).get()
                            if status == 0:
                                logging.info('%s %s old password %s' % (s.server_name,s.ipaddr, s.password ))
                                s.password = s.new_password
                                s.change_password_time = django.utils.timezone.now()
                                s.change_password_tag = 0
                                s.save()
                            else:
                                logging.info('%s %s update password failed ' % (s.server_name,s.ipaddr ))
                        p.close()
                        p.join()
                    elif action_type.strip() == 'reset_password_tag':
                        cmdb_server_list = models.Server.objects.all()
                        for s in cmdb_server_list:
                            s.change_password_tag = 1
                            s.save()
                    elif action_type.strip() == 'connection_check':
                        server_ids = request.POST.getlist('checkbox_list')
                        cmdb_server_list = models.Server.objects.filter(id__in = server_ids)
                        p = Pool(multiprocessing.cpu_count())
                        for s in cmdb_server_list:
                            status = p.apply_async(execute_cmd, args=(s,'echo 0',)).get()
                            logging.info('check ssh connnection result : %s ' % status[0])
                            if int(status[0]) == 0:
                                s.ssh_check=0
                            else:
                                s.ssh_check=1
                            s.save()
                        p.close()
                        p.join()
                    elif action_type.strip() == 'export_excel':
                        response = HttpResponse(content_type='application/vnd.ms-excel')
                        exportTime = django.utils.timezone.now()
                        exportTimeStr  = exportTime.strftime("%Y%m%d")
                        file_name = 'account_info_%s' % exportTimeStr
                        response['Content-Disposition'] = 'attachment;filename=%s.xls' % file_name
                        wb = xlwt.Workbook(encoding = 'utf-8')
                        group_name_list = models.ServerGroup.objects.values('group_name')
                        for r in group_name_list:
                            sheet = wb.add_sheet(r['group_name'])
                            #1st line
                            sheet.write(0,0, 'Server Name')
                            sheet.write(0,1, 'Ip Address')
                            sheet.write(0,2, 'Port')
                            sheet.write(0,3, 'Username')
                            sheet.write(0,4, 'Password')
                            sheet.write(0,5, 'New Password')

                            row = 1
                            for s in models.Server.objects.filter(server_group__group_name=r['group_name']):
                                sheet.write(row,0, s.server_name)
                                sheet.write(row,1, s.ipaddr)
                                sheet.write(row,2, s.port)
                                sheet.write(row,3, s.username)
                                sheet.write(row,4, s.password)
                                sheet.write(row,5, s.new_password)

                                row=row + 1

                        else:
                            sheet = wb.add_sheet('others')
                            #1st line
                            sheet.write(0,0, 'Server Name')
                            sheet.write(0,1, 'Ip Address')
                            sheet.write(0,2, 'Port')
                            sheet.write(0,3, 'Username')
                            sheet.write(0,4, 'Password')
                            sheet.write(0,5, 'New Password')

                            row = 1
                            for s in models.Server.objects.filter(server_group__group_name=None):
                                sheet.write(row,0, s.server_name)
                                sheet.write(row,1, s.ipaddr)
                                sheet.write(row,2, s.port)
                                sheet.write(row,3, s.username)
                                sheet.write(row,4, s.password)
                                sheet.write(row,5, s.new_password)

                                row=row + 1

                        output = StringIO.StringIO()
                        wb.save(output)
                        output.seek(0)
                        response.write(output.getvalue())
                        return response
            return HttpResponseRedirect("/cmdb_main/?page=%s&group_name=%s&server_name=%s" % (page,group_name,server_name))
    except Exception,e:
        logging.info(str(e))

