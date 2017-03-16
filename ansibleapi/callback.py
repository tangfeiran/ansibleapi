#coding:utf8
import json
from ansible import constants as C
from ansible.plugins.callback.default import CallbackModule

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

class ExtendCallback(CallbackModule):
    """重写console输出日志"""

    # 重写2.0版本正确stdout
    def v2_runner_on_ok(self, result):

        if self._play.strategy == 'free' and self._last_task_banner != result._task._uuid:
            self._print_task_banner(result._task)

        self._clean_results(result._result, result._task.action)
        #delegated_vars = result._result.get('_ansible_delegated_vars', None)
        delegated_vars = self._dump_results(result._result)
        #delegated_vars = result._result
        #n_delegated_vars = self._dump_results(result)
        #print n_delegated_vars
        self._clean_results(result._result, result._task.action)
        if result._task.action in ('include', 'include_role'):
            return
        elif result._result.get('changed', False):
            if delegated_vars:
                # 自定义输出
                zdy_msg = self.zdy_stdout(json.loads(delegated_vars))
                if zdy_msg:
                    msg = "changed: [%s]%s" % (result._host.get_name(), zdy_msg)
                else:
                    msg = "changed: [%s -> %s]" % (result._host.get_name(), delegated_vars)
            else:
                msg = "changed: [%s]" % result._host.get_name()
            color = C.COLOR_CHANGED
        # 判断是否是第一步 setup
        elif result._result.get('ansible_facts',False):
            msg = "ok: [ %s | %s ]" % (str(result._host),str(result._host.get_groups()))
            color = C.COLOR_OK
        else:
            if delegated_vars:
                # 自定义输出
                zdy_msg = self.zdy_stdout(json.loads(delegated_vars))
                if zdy_msg:
                    msg = "ok: [%s]%s" % (result._host.get_name(), zdy_msg)
                else:
                    msg = "ok: [%s -> %s]" % (result._host.get_name(), delegated_vars)
            else:
                msg = "ok: [%s]" % result._host.get_name()
            color = C.COLOR_OK

        if result._task.loop and 'results' in result._result:
            self._process_items(result)
        else:
            self._display.display(msg, color=color)

        self._handle_warnings(result._result)

    # 自定义输出,格式清晰一些
    def zdy_stdout(self,result):
        msg = ''
        if result.get('delta',False):
            msg += u'\t执行时间:%s'%result['delta']
        if result.get('cmd', False):
            msg += u'\n执行命令:%s'%result['cmd']
        if result.get('stderr',False):
            msg += u'\n错误输出:\n%s'%result['stderr']
        if result.get('stdout',False):
            msg += u'\n正确输出:\n%s'%result['stdout']
        if result.get('warnings',False):
            msg += u'\n警告:%s'%result['warnings']
        return msg

