#coding:utf-8
from ansible.utils.display import Display

class MyDisplay(Display):

    def __init__(self, func):
        '''
        func 为需要增加的display方式的函数，接受一个参数msg
        :param func:
        '''
        super(MyDisplay, self).__init__()
        self.func = func

    def display(self, msg, color=None, stderr=False, screen_only=False, log_only=False):
        super(MyDisplay, self).display(msg, color=None, stderr=False, screen_only=False, log_only=False)
        self.func(msg)