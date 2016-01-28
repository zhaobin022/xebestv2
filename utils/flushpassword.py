#! /usr/bin/env python
# -*- coding: utf-8 -*-

from random import choice
import re
import string
import sys
import pexpect
import logging
from django.utils import timezone
import django.utils.timezone


def GenPassword(length=32,chars=string.ascii_letters+string.digits):
    return ''.join([choice(chars) for i in range(length)])

               #s.flush_password_time=timezone.now()
      #          s.save()
       #         localtime = timezone.localtime(timezone.now())

def ssh_cmd(s,newpassword):
    timeout = 35
    ret = -1
    print 'ssh -p%s %s@%s' % (s.port,s.username,s.ipaddr)
    ssh = pexpect.spawn('ssh -p%s %s@%s' % (s.port,s.username,s.ipaddr))
    try:
        i = ssh.expect(['password:', 'continue connecting (yes/no)?'], timeout=timeout)
        logging.info(10)
        if i == 0 :
            ssh.sendline(s.password)
        elif i == 1:
            ssh.sendline('yes\n')
            ssh.expect('password: ',timeout=timeout)
            ssh.sendline(s.password)
        ssh.sendline('passwd')

 #       r = ssh.read()
        ssh.expect('New password:',timeout=timeout)
        ssh.sendline(newpassword)
        ssh.expect('Retype new password:',timeout=timeout)
        ssh.sendline(newpassword)
        ssh.expect('#',timeout=timeout)
        ssh.sendline('exit')

        pattern = re.compile(r'.*tokens updated successfully.*',re.S)
        result = ssh.before
        logging.info(result)
        if pattern.match(result).group():
            ret = 0

            print s.change_password_tag,'password tag'
        else:
            ret = 1
    except pexpect.EOF:
        ssh.close()
        ret = 1
    except pexpect.TIMEOUT:
        ssh.close()
        ret = 1
    except Exception,e:  
        logging.info(str(e))
        ret = 1
    return ret 

if __name__ == '__main__':
    print GenPassword()
#try:
#
#    conn=MySQLdb.connect(host='localhost',user='root',passwd='root',port=3306,charset="utf8")
#    cur=conn.cursor()
#    conn.select_db('xianyi')
#    
#    cur.execute('select * from app01_server where password="000000"')
#    results=cur.fetchall()
#    for i in results:
#        ip = i[2]
#        password = i[5]
#        print ip,password,GenPassword()
#    
#    cur.close()
#    conn.close()
#    
#except MySQLdb.Error,e:
#    print "Mysql Error %d: %s" % (e.args[0], e.args[1])


#f = open('ip.txt')
#for l in f:
#    row = l.strip().split()
#    status = ssh_cmd(row[0],row[1],row[2])
#    print row,status
#
#f.close()


#class S:
#    pass
#
#
#s = S()
#s.port = '22'
#s.ipaddress = '192.168.26.205'
#s.password = 'test'
#
#ssh_cmd(s)
