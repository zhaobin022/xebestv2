#!/usr/bin/python
# -*- coding:utf-8 -*-
import tty
import select
from prettytable import PrettyTable
import datetime
import paramiko
import socket
from paramiko.py3compat import u

import sys

reload(sys)
sys.setdefaultencoding('utf8')

import os
import re
import time
import datetime
import textwrap
import getpass
import readline
import django
import paramiko
import errno
import pyte
import operator
import struct, fcntl, signal, socket, select
from io import open as copen
import uuid


try:
    import termios
    import tty
except ImportError:
    print '\033[1;31m仅支持类Unix系统 Only unix like supported.\033[0m'
    time.sleep(3)
    sys.exit()


class Tty(object):
    """
    A virtual tty class
    一个虚拟终端类，实现连接ssh和记录日志，基类
    """
    def __init__(self,main_obj,server_obj):
        self.main_obj = main_obj
        self.server_obj = server_obj
        self.ip = server_obj.ipaddr
        self.port = server_obj.port
        self.username = server_obj.username
        self.password = server_obj.password
        self.ssh = None
        self.channel = None
        self.remote_ip = ''
        self.login_type = 'ssh'
        self.vim_flag = False
        self.vim_end_pattern = re.compile(r'\x1b\[\?1049', re.X)
        self.vim_data = ''
        self.stream = None
        self.screen = None
        self.__init_screen_stream()

    def __init_screen_stream(self):
        """
        初始化虚拟屏幕和字符流
        """
        self.stream = pyte.ByteStream()
        self.screen = pyte.Screen(80, 24)
        self.stream.attach(self.screen)

    @staticmethod
    def is_output(strings):
        newline_char = ['\n', '\r', '\r\n']
        for char in newline_char:
            if char in strings:
                return True
        return False

    @staticmethod
    def command_parser(command):
        """
        处理命令中如果有ps1或者mysql的特殊情况,极端情况下会有ps1和mysql
        :param command:要处理的字符传
        :return:返回去除PS1或者mysql字符串的结果
        """
        result = None
        match = re.compile('\[?.*@.*\]?[\$#]\s').split(command)
        if match:
            # 只需要最后的一个PS1后面的字符串
            result = match[-1].strip()
        else:
            # PS1没找到,查找mysql
            match = re.split('mysql>\s', command)
            if match:
                # 只需要最后一个mysql后面的字符串
                result = match[-1].strip()
        return result

    def deal_command(self, data):
        """
        处理截获的命令
        :param data: 要处理的命令
        :return:返回最后的处理结果
        """
        command = ''
        try:
            self.stream.feed(data)
            # 从虚拟屏幕中获取处理后的数据
            for line in reversed(self.screen.buffer):
                line_data = "".join(map(operator.attrgetter("data"), line)).strip()
                if len(line_data) > 0:
                    parser_result = self.command_parser(line_data)
                    if parser_result is not None:
                        # 2个条件写一起会有错误的数据
                        if len(parser_result) > 0:
                            command = parser_result
                    else:
                        command = line_data
                    break
        except Exception:
            pass
        # 虚拟屏幕清空
        self.screen.reset()
        return command


    def get_connection(self):
        """
        获取连接成功后的ssh
        """

        # 发起ssh连接请求 Make a ssh connection
        ssh = paramiko.SSHClient()
        # ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(self.ip,
                        self.port,
                        username=self.username,
                        password=self.password,
                        allow_agent=False,
                        look_for_keys=False)
        except (paramiko.ssh_exception.AuthenticationException, paramiko.ssh_exception.SSHException):
            print 'auth failed '
        except socket.error:
            print 'socket error'
        else:
            self.ssh = ssh
            return ssh

class SshTty(Tty):
    """
    A virtual tty class
    一个虚拟终端类，实现连接ssh和记录日志
    """

    @staticmethod
    def get_win_size():
        """
        This function use to get the size of the windows!
        获得terminal窗口大小
        """
        if 'TIOCGWINSZ' in dir(termios):
            TIOCGWINSZ = termios.TIOCGWINSZ
        else:
            TIOCGWINSZ = 1074295912L
        s = struct.pack('HHHH', 0, 0, 0, 0)
        x = fcntl.ioctl(sys.stdout.fileno(), TIOCGWINSZ, s)
        return struct.unpack('HHHH', x)[0:2]

    def set_win_size(self, sig, data):
        """
        This function use to set the window size of the terminal!
        设置terminal窗口大小
        """
        try:
            win_size = self.get_win_size()
            self.channel.resize_pty(height=win_size[0], width=win_size[1])
        except Exception:
            pass

    def posix_shell(self):
        """
        Use paramiko channel connect server interactive.
        使用paramiko模块的channel，连接后端，进入交互式
        """
        old_tty = termios.tcgetattr(sys.stdin)
        pre_timestamp = time.time()
        data = ''
        input_mode = False
        try:
            tty.setraw(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
            self.channel.settimeout(0.0)

            while True:
                try:
                    r, w, e = select.select([self.channel, sys.stdin], [], [])
                    flag = fcntl.fcntl(sys.stdin, fcntl.F_GETFL, 0)
                    fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, flag|os.O_NONBLOCK)
                except Exception:
                    pass

                if self.channel in r:
                    try:
                        x = self.channel.recv(10240)
                        if len(x) == 0:
                            break

                        index = 0
                        len_x = len(x)
                        while index < len_x:
                            try:
                                n = os.write(sys.stdout.fileno(), x[index:])
                                sys.stdout.flush()
                                index += n
                            except OSError as msg:
                                if msg.errno == errno.EAGAIN:
                                    continue

                        self.vim_data += x
                        if input_mode:
                            data += x

                    except socket.timeout:
                        pass

                if sys.stdin in r:
                    try:
                        x = os.read(sys.stdin.fileno(), 4096)
                    except OSError:
                        pass
                    input_mode = True
                    if self.is_output(str(x)):
                        # 如果len(str(x)) > 1 说明是复制输入的
                        if len(str(x)) > 1:
                            data = x
                        match = self.vim_end_pattern.findall(self.vim_data)
                        if match:
                            if self.vim_flag or len(match) == 2:
                                self.vim_flag = False
                                self.main_obj.deal_audit_log(data,self.server_obj)
                            else:
                                self.vim_flag = True
                        elif not self.vim_flag:
                            self.vim_flag = False
                            data = self.deal_command(data)[0:200]
                            if data is not None:
                                self.main_obj.deal_audit_log(data,self.server_obj)
                        data = ''
                        self.vim_data = ''
                        input_mode = False

                    if len(x) == 0:
                        break
                    self.channel.send(x)

        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)

    def connect(self):
        """
        Connect server.
        连接服务器
        """
        # 发起ssh连接请求 Make a ssh connection
        ssh = self.get_connection()

        transport = ssh.get_transport()
        transport.set_keepalive(30)
        transport.use_compression(True)

        # 获取连接的隧道并设置窗口大小 Make a channel and set windows size
        global channel
        win_size = self.get_win_size()
        # self.channel = channel = ssh.invoke_shell(height=win_size[0], width=win_size[1], term='xterm')
        self.channel = channel = transport.open_session()
        channel.get_pty(term='xterm', height=win_size[0], width=win_size[1])
        channel.invoke_shell()
        try:
            signal.signal(signal.SIGWINCH, self.set_win_size)
        except:
            pass

        self.posix_shell()

        # Shutdown channel socket
        channel.close()
        ssh.close()






class JumpServer(object):
    def __init__(self):
        self.basedir = (os.path.sep).join(os.path.abspath(__file__).split(os.path.sep)[:-2])
        sys.path.append(self.basedir)
        os.environ['DJANGO_SETTINGS_MODULE'] ='xebest.settings'
        import django
        django.setup()
        from cmdb import models
        self.models = models
        self.username = os.environ.get('SUDO_USER')

    def display_group(self,):
        group_query_set = self.user.server_group.all()
        self.group_dic = {}
        x = PrettyTable(["Id","GroupName","Count"])
        for i,g in enumerate(group_query_set):
            self.group_dic[i] = [g.id,g.group_name]
            x.add_row([i,g.group_name,g.servers.count()])
        print x

    def display_server(self,group_id,search=False,search_value=None):
        #server_query_set = self.models.Server.objects.filter(server_group_id = group_id)
        if search:
            server_query_set = self.models.ServerGroup.objects.get(id=group_id).servers.filter(server_name__icontains = search_value)
        else:
            server_query_set = self.models.ServerGroup.objects.get(id=group_id).servers.all()
        self.server_dic = {}
        x = PrettyTable(["Id","ServerName","IpAddress" ,"Port"])
        for i,s in enumerate(server_query_set):
            self.server_dic[i] = s
            x.add_row([i,s.server_name,s.ipaddr,s.port])
        print x


    def auth(self):
        username_list = self.models.OsUser.objects.values_list('username',flat=True)
        if self.username not in username_list:
            try:
                raw_input( '''You don't have permission to login to this jumpserver ''')
                sys.exit(1)
            except Exception , e:
                sys.exit(1)
              #  logging.info(str(e))
            finally:
                sys.exit(1)
        else:
            self.user = self.models.OsUser.objects.get(username = self.username)


    def run(self):
        self.auth()
        while True:
            self.display_group()
            try:
                group_index = raw_input("\r\n\033[32;1mPlease input the group index or exit to quit the jumpserver: \033[0m\r\n")
            except KeyboardInterrupt:
                break
            except Exception,e:
                break
            if group_index.isdigit() and int(group_index) in self.group_dic.keys():
                search_tag = False
                search_value=''
                while True:

                    if search_tag:
                        self.display_server(self.group_dic[int(group_index)][0],search=True,search_value=search_value)
                        search_tag=False
                    else:
                        self.display_server(self.group_dic[int(group_index)][0])
                    try:
                        server_index = raw_input("\r\n\033[32;1mPlease input the server index or  exit to return to the group list or / for search server name ! \n\033[0m\r\n")
                    except KeyboardInterrupt:
                        break
                    except Exception,e:
                        break
                    if server_index.isdigit() and int(server_index) in self.server_dic.keys():
                        s = self.server_dic[int(server_index)]
                        self.login(s)
                    elif server_index.strip() == 'exit':
                        break
                    elif server_index.strip().startswith('/'):
                        search_tag = True
                    else:
                        print "\r\n\033[31;1mPlase input the right server index  or input exit return to group list !\033[0m\r\n"
                    search_value =  server_index.strip().replace('/','',1)
            elif group_index == 'exit':
                sys.exit()
            else:
                print '\r\n\033[31;1mPlease input the right group id or input exit to exit the jumpserver !\033[0m\r\n'

    def deal_audit_log(self,cmd,s):
        msg = 'server name : %s , ip : %s , user : %s , cmd : %s ' % (s.server_name,s.ipaddr,self.username,cmd)
        self.models.JumpServerAudit.objects.create(username=self.username,content=msg)

    def login(self,s):
        try:
            self.unsupport_cmd_list = ['rz','sz']
            self.deal_audit_log('*** Session Opened ***',s)
            ssh_obj = SshTty(self,s)
            ssh_obj.connect()
            self.deal_audit_log('*** Session Closed ***',s)
        except Exception,e:
            print '\r\n\033[31;1mLogin fail Please contact the server admin !!\033[0m\r\n'
            print str(e)
            return



    def posix_shell(self,chan,s):
        import select
        import termios
        oldtty = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
            chan.settimeout(0.0)


            cmd = ''
            tab_input_flag = False
            while True:
                r, w, e = select.select([chan, sys.stdin], [], [])

                if chan in r:
                    try:

                        x = u(chan.recv(1024))
                        if tab_input_flag:
                            cmd +=''.join(x[:10])
                            tab_input_flag = False
                        if len(x) == 0:
                            sys.stdout.write('\r\n\033[32;1m*** Session Closed ***\033[0m\r\n')
                            self.deal_audit_log('*** Session Closed ***',s)
                            break

                        sys.stdout.write(x)
                        sys.stdout.flush()

                    except socket.timeout:
                        pass
                    except UnicodeDecodeError,e:
                        pass
                if sys.stdin in r:
                    x = sys.stdin.read(1)
                    if len(x) == 0:
                        break
                    if not x == '\r':
                        try:
                            cmd +=x
                        except UnicodeDecodeError,e:
                            pass
                        except UnicodeEncodeError,e:
                            pass
                    else:
                        if len(cmd.strip())>0:
                            self.deal_audit_log(cmd,s)
                        if cmd in self.unsupport_cmd_list:
                            x="...Operation is not supported!\r\n"
                        cmd=''

                    if x == '\t':
                        tab_input_flag = True
                    chan.send(x)

            #f.close()
            #print cmd_list
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)


    # thanks to Mike Looijmans for this code
    def windows_shell(self,chan):
        import threading

        sys.stdout.write("Line-buffered terminal emulation. Press F6 or ^Z to send EOF.\r\n\r\n")

        def writeall(sock):
            while True:
                data = sock.recv(256)
                if not data:
                    sys.stdout.write('\r\n\033[32;1m*** Session closed ***\033[0m\r\n\r\n')
                    sys.stdout.flush()
                    break
                sys.stdout.write(data)
                sys.stdout.flush()

        writer = threading.Thread(target=writeall, args=(chan,))
        writer.start()

        try:
            while True:
                d = sys.stdin.read(1)
                if not d:
                    break
                chan.send(d)
        except EOFError:
            # user hit ^Z or F6
            pass

if __name__ == '__main__':
    j = JumpServer()
    j.run()
