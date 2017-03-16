#coding:utf8
import json
from ansible import constants as C
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.utils.ssh_functions import check_for_controlpersist

# 调用自定义Inventory
from inventory import ExtendInventory as Inventory 
from callback import ExtendCallback

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

class ExtendPlaybookExecutor(PlaybookExecutor):
    
    '''重写PlayBookExecutor, 增加自定义callback'''
    def __init__(self, playbooks, inventory, variable_manager, loader, options, passwords, stdout_callback=None):
        super(ExtendPlaybookExecutor, self).__init__(playbooks, inventory, variable_manager, loader, options, passwords)
        if stdout_callback:
            self._tqm._stdout_callback = stdout_callback

class PlayBookJob(object):
  '''封装一个playbook接口,提供给外部使用'''
  def __init__(self,playbooks,host_list,remote_user='bbs',passwords='null',group_name='all',ask_pass=False,forks=5,ext_vars=None):
    self.playbooks = playbooks
    self.host_list = host_list
    self.remote_user  = remote_user
    self.passwords = dict(conn_pass=passwords)
    self.group_name = group_name
    self.ask_pass  = ask_pass
    self.forks     = forks
    self.connection='smart'
    self.ext_vars  = ext_vars

    ## 用来加载解析yaml文件或JSON内容,并且支持vault的解密
    self.loader    = DataLoader()

    # 管理变量的类，包括主机，组，扩展等变量，之前版本是在 inventory中的
    self.variable_manager = VariableManager()

    # 根据inventory加载对应变量
    self.inventory = Inventory(loader=self.loader, 
                               variable_manager=self.variable_manager,
                               group_name=self.group_name,  # 项目名对应组名,区分当前执行的内容
                               ext_vars=self.ext_vars,
                               host_list=self.host_list)

    self.variable_manager.set_inventory(self.inventory)

    # 初始化需要的对象1
    self.Options = namedtuple('Options',
                             ['connection',
                             'remote_user',
                             'ask_sudo_pass',
                             'verbosity',
                             'ask_pass', 
                             'module_path', 
                             'forks', 
                             'become', 
                             'become_method', 
                             'become_user', 
                             'check',
                             'listhosts', 
                             'listtasks', 
                             'listtags', 
                             'syntax',
                             'sudo_user',
                             'sudo'
                             ])

    # 初始化需要的对象2
    self.options = self.Options(connection=self.connection, 
                                remote_user=self.remote_user,
                                ask_pass=self.ask_pass,
                                sudo_user='root',
                                forks=self.forks,
                                sudo='yes',
                                ask_sudo_pass=False,
                                verbosity=5,
                                module_path=None,  
                                become=True, 
                                become_method='sudo', 
                                become_user='root', 
                                check=None,
                                listhosts=None,
                                listtasks=None, 
                                listtags=None, 
                                syntax=None
                               )

    # 初始化console输出
    self.callback = ExtendCallback()

    # 直接开始
    self.run()

  def run(self):
    pb = None
    pb = ExtendPlaybookExecutor(
        playbooks            = self.playbooks,
        inventory            = self.inventory,
        variable_manager     = self.variable_manager,
        loader               = self.loader,
        options              = self.options,
        passwords            = self.passwords,
        stdout_callback      = self.callback
    )
    result = pb.run()

# daemo
if __name__ == "__main__":
    PlayBookJob(playbooks=['/tmp/test.yml'],
                host_list=['172.16.10.54', '172.16.10.53'],
                remote_user='root',
                group_name="test",
                forks=20,
                ext_vars=None,
                passwords='123456'
                )
