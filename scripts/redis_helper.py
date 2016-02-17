__author__ = 'zhaobin022'


import redis
import random
class RedisHelper(object):
    def __init__(self):
        self.r = redis.Redis(host='192.168.26.67', port=6379)

    def batchInsertKey(self):
        for i in range(1000000):
            k = '%040d' % i
            v = ''
            self.r.set(k,v)
            self.r.delete()
    def phase_two(self):
        for i in range(900000):
            k = '%020d' % random.randint(0,1000000)
            v =  'b' * 130
            self.r.set(k,v)
    def phase_three(self):
        for i in range(900000):
            k = '%020d' % random.randint(0,1000000)
            v =  'c' * 210
            self.r.set(k,v)
    def printRedisInfo(self):
        info = self.r.info()
        for key in info:
            print "%s: %s" % (key, info[key])

    def loopKey(self):
        self.unexpireed_count = 0
        self.total_count = 0
        self.expired_count = 0
        for k in self.r.keys():
            if not self.r.ttl(k):
                self.unexpireed_count +=1
            else:
               # print 'expireed_key',k
                self.expired_count += 1
            self.total_count += 1
            print self.total_count
        print 'unexpored count count',self.unexpireed_count
        print 'total count',self.total_count
        print 'expired count',self.expired_count
    def run(self):
        #self.loopKey()
        self.batchInsertKey()
        #self.printRedisInfo()



r = RedisHelper()
r.run()
