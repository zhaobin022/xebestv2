# Register your models here.

from django.contrib import admin
from cmdb.models import *

# Register your models here.

class LoggerAdmin(admin.ModelAdmin):
    def get_server_name(self,obj):
        if obj.operation == 6:return 'unzip log'
        return obj.server.server_name
    list_display = ('id','operation','get_server_name','username','status','description','happened_time')
#    list_filter = ('operation','username','happened_time')
    list_filter = ('operation','username','happened_time','server__server_name','server__app__app_name')
    search_fields = ('operation','username')
    readonly_fields = Logger._meta.get_all_field_names()


class BackupAdmin(admin.ModelAdmin):
    def get_app_name(self,obj):
        return obj.app.app_name
    list_display = ('id','backup_name','get_app_name','status')
#    list_filter = ('operation','username','happened_time')
    list_filter = ('app__app_name','backup_time')
class ServerAdmin(admin.ModelAdmin):
    def get_group_name(self,obj):
        if obj.server_group:
            return obj.server_group.group_name
        else:
            return 'not in any group'
    list_display = ('id','server_name','ipaddr','port','username','password','get_group_name')
#    list_filter = ('operation','username','happened_time')
    search_fields = ('server_name','ipaddr')


class TaskLogAdmin(admin.ModelAdmin):
    def get_task_type_name(self,obj):
        return obj.get_task_type_display()
    list_display = ('id','get_task_type_name')
 #   readonly_fields = TaskLog._meta.get_all_field_names()

    #list_display = ('id',)
#    list_filter = ('operation','username','happened_time')
class OsUserAdmin(admin.ModelAdmin):
    list_display = ('id','username')

admin.site.register(Server,ServerAdmin)
admin.site.register(App)
admin.site.register(ServerGroup)
admin.site.register(TaskLog,TaskLogAdmin)
admin.site.register(Backup,BackupAdmin)
admin.site.register(Logger,LoggerAdmin)
admin.site.register(OsUser,OsUserAdmin)
