#!/usr/bin/env python
#coding=utf8
import pika, threading, uuid
 
#自定义线程类，继承threading.Thread
class MyThread(threading.Thread):
    def __init__(self, func, num):
        super(MyThread, self).__init__()
        self.func = func
        self.num = num
 
    def run(self):
        print " [x] Requesting increase(%d)" % self.num
        response = self.func(self.num)
        print " [.] increase(%d)=%d" % (self.num, response)
 
#控制中心类
class Center(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='localhost'))
 
        self.channel = self.connection.channel()
 
        #定义接收返回消息的队列
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
 
        self.channel.basic_consume(self.on_response,
                                   no_ack=True,
                                   queue=self.callback_queue)
 
        #返回的结果都会存储在该字典里
        self.response = {}
 
    #定义接收到返回消息的处理方法
    def on_response(self, ch, method, props, body):
        self.response[props.correlation_id] = body
 
    def request(self, n):
        corr_id = str(uuid.uuid4())
        self.response[corr_id] = None
 
        #发送计算请求，并设定返回队列和correlation_id
        self.channel.basic_publish(exchange='',
                                   routing_key='compute_queue',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = corr_id,
                                         ),
                                   body=str(n))
        #接收返回的数据
        while self.response[corr_id] is None:
            self.connection.process_data_events()
        return int(self.response[corr_id])
 
center = Center()
#发起5次计算请求
nums= [10, 20, 30, 40 ,50]
threads = []
for num in nums:
    threads.append(MyThread(center.request, num))
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()


print threads