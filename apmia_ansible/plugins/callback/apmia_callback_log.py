# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: default
    type: stdout
    short_description: Ansible Screen Output and Create log file
    version_added: historical
    description:
        - This is the CA apmia output callback for ansible-playbook.
    extends_documentation_fragment:
      - default_callback
    requirements:
      - set as stdout in configuration
'''

from ansible import constants as C
from ansible.playbook.task_include import TaskInclude
from ansible.plugins.callback import CallbackBase
from ansible.utils.color import colorize, hostcolor
from datetime import datetime
import os
import re
import sys
import thread
import time
import multiprocessing
import threading
import os.path
import string




class CallbackModule(CallbackBase):

    '''
    This is the default callback interface, which simply prints messages
    to stdout when new callback events are received.
    '''

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'apmia_callback_log'
    global print_star
    global f
    global fil
    global host_list
    host_list = []
    f = open('apmia_ansible.log', "a")
    if os.path.exists('temp_abc') == True:
        os.remove('temp_abc')
    if os.path.exists('report.log') == True:
        os.remove('report.log')
    if os.path.exists('comment_temp') == True:
        os.remove('comment_temp')
    if os.path.exists('msg_temp') == True:
        os.remove('msg_temp')

    def __init__(self):

        self._play = None
        super(CallbackModule, self).__init__()

    def print_star(msg):
        sys.stdout.write("\033[K")
        while True:
                sys.stdout.flush()
                print("......", end='')
                time.sleep(0.5)
		if msg != "stop":
			break
        print(end="\r")
        sys.stdout.write("\033[K")

    def v2_runner_on_failed(self, command_result, ignore_errors=False):
	
	fil = open('temp_abc', "a")
        t1 = threading.Thread(target=print_star, args=("start",))
       	t1.start()

        dele_variables = command_result._result.get('_ansible_dele_variables', None)

        if self._play.strategy == 'free' and self._last_task_banner != command_result._task._uuid:
            self._print_task_banner(command_result._task)

        self._handle_exception(command_result._result)
        self._handle_warnings(command_result._result)

        if command_result._task.loop and 'results' in command_result._result:
            self._process_items(command_result)

        else:
            if dele_variables:
		f.writelines("%s-----fatal: [%s -> %s]: FAILED! => %s\n" % (datetime.now(), command_result._host.get_name(), dele_variables['ansible_host'], self._dump_results(command_result._result)))
            else:
		f.writelines("%s-----fatal: [%s]: FAILED! => %s\n" % (datetime.now(), command_result._host.get_name(), self._dump_results(command_result._result)))
	fil.writelines("\n%s Fail %s" % (command_result._host.get_name(), self._dump_results(command_result._result)))
	fil.close()

        if ignore_errors:
            self._display.display("...ignoring", color=C.COLOR_SKIP)
	    f.writelines("%s-----...ignoring\n" % (datetime.now()))

        t1 = threading.Thread(target=print_star, args=("stop",))

    def v2_runner_on_ok(self, command_result):

        t2 = threading.Thread(target=print_star, args=("start",))
       	t2.start()

        dele_variables = command_result._result.get('_ansible_dele_variables', None)

        if self._play.strategy == 'free' and self._last_task_banner != command_result._task._uuid:
            self._print_task_banner(command_result._task)

        if isinstance(command_result._task, TaskInclude):
            return
        elif command_result._result.get('changed', False):
            if dele_variables:
                msg = "changed: [%s -> %s]" % (command_result._host.get_name(), dele_variables['ansible_host'])
                msg1 = ""
            else:
                msg = "changed: [%s]" % command_result._host.get_name()
                msg1 = ""
            color = C.COLOR_CHANGED
        else:
            if dele_variables:
                msg = "ok: [%s -> %s]" % (command_result._host.get_name(), dele_variables['ansible_host'])
		msg1=""
            else:
                msg = "ok: [%s]" % command_result._host.get_name()
		msg1=""
            color = C.COLOR_OK

        self._handle_warnings(command_result._result)

        if command_result._task.loop and 'results' in command_result._result:
            self._process_items(command_result)
        else:
            if (self._display.verbosity > 0 or '_ansible_verbose_always' in command_result._result) and '_ansible_verbose_override' not in command_result._result:
                if command_result._task.action == 'debug' and 'changed' in command_result._result:
                    del command_result._result['changed']
                msg += " => %s" % (self._dump_results(command_result._result),)
                msg1 = "%s" % (self._dump_results(command_result._result),)
	    if msg1 != "":
	            self._display.display(msg1, color=color)
	    f.writelines("%s-----%s\n" % (datetime.now(), msg))
        t2 = threading.Thread(target=print_star, args=("stop",))

    def v2_runner_on_skipped(self, command_result):
        t3 = threading.Thread(target=print_star, args=("start",))
       	t3.start()
        if self._plugin_options.get('show_skipped_hosts', C.DISPLAY_SKIPPED_HOSTS):  # fallback on constants for inherited plugins missing docs

            if self._play.strategy == 'free' and self._last_task_banner != command_result._task._uuid:
                self._print_task_banner(command_result._task)

            if command_result._task.loop and 'results' in command_result._result:
                self._process_items(command_result)
            else:
                msg = "skipping: [%s]" % command_result._host.get_name()
                if (self._display.verbosity > 0 or '_ansible_verbose_always' in command_result._result) and '_ansible_verbose_override' not in command_result._result:
                    msg += " => %s" % self._dump_results(command_result._result)
                f.writelines("%s-----%s\n" % (datetime.now(), msg))
        t3 = threading.Thread(target=print_star, args=("stop",))

    def v2_runner_on_unreachable(self, command_result):
	fil = open('temp_abc', "a")
        t4 = threading.Thread(target=print_star, args=("start",))
       	t4.start()
        if self._play.strategy == 'free' and self._last_task_banner != command_result._task._uuid:
            self._print_task_banner(command_result._task)

        dele_variables = command_result._result.get('_ansible_dele_variables', None)
        if dele_variables:
	    f.writelines("fatal: [%s -> %s]: UNREACHABLE! => %s\n" % (command_result._host.get_name(), dele_variables['ansible_host'], self._dump_results(command_result._result)))
        else:
	    f.writelines("fatal: [%s]: UNREACHABLE! => %s\n" % (command_result._host.get_name(), self._dump_results(command_result._result)))
	fil.writelines("\n%s Unreach %s" % (command_result._host.get_name(), self._dump_results(command_result._result)))
	fil.close()
        t4 = threading.Thread(target=print_star, args=("stop",))

    def v2_playbook_on_no_hosts_matched(self):
        t5 = threading.Thread(target=print_star, args=("start",))
       	t5.start()
        self._display.display("skipping: no hosts matched", color=C.COLOR_SKIP)
	f.writelines("%s-----skipping: no hosts matched\n" % (datetime.now()))
        t5 = threading.Thread(target=print_star, args=("stop",))

    def v2_playbook_on_no_hosts_remaining(self):
        t6 = threading.Thread(target=print_star, args=("start",))
       	t6.start()
	f.writelines("%s-----NO MORE HOSTS LEFT\n" % (datetime.now()))
        t6 = threading.Thread(target=print_star, args=("stop",))

    def v2_playbook_on_task_start(self, task, is_conditional):
        t7 = threading.Thread(target=print_star, args=("start",))
       	t7.start()

        if self._play.strategy != 'free':
	    f.writelines("%s-----%s\n" % (datetime.now(), task))
        t7 = threading.Thread(target=print_star, args=("stop",))

    def _print_task_banner(self, task):
        t8 = threading.Thread(target=print_star, args=("start",))
       	t8.start()
        args = ''
        if not task.no_log and C.DISPLAY_ARGS_TO_STDOUT:
            args = u', '.join(u'%s=%s' % a for a in task.args.items())
            args = u' %s' % args
	f.writelines(u"%s-----TASK [%s%s]\n" % (datetime.now(), task.get_name().strip(), args))
        if self._display.verbosity >= 2:
            path = task.get_path()
            if path:
		f.writelines(u"%s-----task path: %s\n" % (datetime.now(), path))
        self._last_task_banner = task._uuid
        t8 = threading.Thread(target=print_star, args=("stop",))

    def v2_playbook_on_cleanup_task_start(self, task):
        t9 = threading.Thread(target=print_star, args=("start",))
       	t9.start()
	f.writelines("%s-----CLEANUP TASK [%s]\n" % (datetime.now(), task.get_name().strip()))
        t9 = threading.Thread(target=print_star, args=("stop",))

    def v2_playbook_on_handler_task_start(self, task):
        t10 = threading.Thread(target=print_star, args=("start",))
       	t10.start()
	f.writelines("%s-----RUNNING HANDLER [%s]\n" % task.get_name().strip())
        t10 = threading.Thread(target=print_star, args=("stop",))

    def v2_playbook_on_play_start(self, play):
        t11 = threading.Thread(target=print_star, args=("start",))
       	t11.start()
        name = play.get_name().strip()
        if not name:
            msg = u"PLAY"
        else:
            msg = u"PLAY [%s]" % name
        self._play = play
	f.writelines("%s-----%s\n" % (datetime.now(), msg))
        t11 = threading.Thread(target=print_star, args=("stop",))

    def v2_on_file_diff(self, command_result):
        t12 = threading.Thread(target=print_star, args=("start",))
       	t12.start()
        if command_result._task.loop and 'results' in command_result._result:
            for res in command_result._result['results']:
                if 'diff' in res and res['diff'] and res.get('changed', False):
                    diff = self._get_diff(res['diff'])
                    if diff:
			f.writelines("%s-----%s\n" % (datetime.now(), diff))
        elif 'diff' in command_result._result and command_result._result['diff'] and command_result._result.get('changed', False):
            diff = self._get_diff(command_result._result['diff'])
            if diff:
		f.writelines("%s-----%s\n" % (datetime.now(), diff))
        t12 = threading.Thread(target=print_star, args=("stop",))

    def v2_runner_item_on_ok(self, command_result):
        t13 = threading.Thread(target=print_star, args=("start",))
       	t13.start()
        dele_variables = command_result._result.get('_ansible_dele_variables', None)
        if isinstance(command_result._task, TaskInclude):
            return
        elif command_result._result.get('changed', False):
            msg = 'changed'
            color = C.COLOR_CHANGED
        else:
            msg = 'ok'
            color = C.COLOR_OK
        if dele_variables:
            msg += ": [%s -> %s]" % (command_result._host.get_name(), dele_variables['ansible_host'])
        else:
            msg += ": [%s]" % command_result._host.get_name()

        msg += " => (item=%s)" % (self._get_item(command_result._result),)
        if (self._display.verbosity > 0 or '_ansible_verbose_always' in command_result._result) and '_ansible_verbose_override' not in command_result._result:
            msg += " => %s" % self._dump_results(command_result._result)
	f.writelines("%s-----%s\n" % (datetime.now(), msg))
        t13 = threading.Thread(target=print_star, args=("stop",))
    
    def v2_runner_item_on_failed(self, command_result):
        t14 = threading.Thread(target=print_star, args=("start",))
       	t14.start()
        dele_variables = command_result._result.get('_ansible_dele_variables', None)
        self._handle_exception(command_result._result)
        msg = "failed: "
        if dele_variables:
            msg += "[%s -> %s]" % (command_result._host.get_name(), dele_variables['ansible_host'])
        else:
            msg += "[%s]" % (command_result._host.get_name())

        self._handle_warnings(command_result._result)
	f.writelines("%s-----%s (item=%s) => %s\n" % (datetime.now(), msg, self._get_item(command_result._result), self._dump_results(command_result._result)))
        t14 = threading.Thread(target=print_star, args=("stop",))

    def v2_runner_item_on_skipped(self, command_result):
        t15 = threading.Thread(target=print_star, args=("start",))
       	t15.start()
        if self._plugin_options.get('show_skipped_hosts', C.DISPLAY_SKIPPED_HOSTS):  # fallback on constants for inherited plugins missing docs
            msg = "skipping: [%s] => (item=%s) " % (command_result._host.get_name(), self._get_item(command_result._result))
            if (self._display.verbosity > 0 or '_ansible_verbose_always' in command_result._result) and '_ansible_verbose_override' not in command_result._result:
                msg += " => %s" % self._dump_results(command_result._result)
	    f.writelines("%s-----%s\n" % (datetime.now(), msg))
        t15 = threading.Thread(target=print_star, args=("stop",))

    def v2_playbook_on_include(self, included_file):
        t16 = threading.Thread(target=print_star, args=("start",))
       	t16.start()
        msg = 'included: %s for %s' % (included_file._filename, ", ".join([h.name for h in included_file._hosts]))
	f.writelines("%s-----%s\n" % (datetime.now(), msg))
        t16 = threading.Thread(target=print_star, args=("stop",))

    def v2_playbook_on_stats(self, stats):
	max_length = []
	hn = ""
	cn = ""
	st = ""
	outp = ""
	mt = []
	change_host_list = []
#########################################################################################################################
        if os.path.exists('msg_temp') == True:
		mt1=open('msg_temp')
		max_length_line = len(max(open('msg_temp', 'r'), key=len))
		if max_length_line+10 >= 168:
		        max_length_line = 158
		for line in mt1:
			mt.append(line.split(None, 1))
		if len(mt) != 0:
			for itm in range(len(mt)):
				change_host_list.append(mt[itm][0])
			change_host_list = set(change_host_list)
			print("\n")
			f.writelines("%s\n" % (datetime.now()))
			for i in range(max_length_line+10):
				print("\033[34m-\033[0m", end = '')
				f.write("-")
			print("\033[36m\nConfiguration Changed in Each Host\033[0m")
			f.writelines("\nConfiguration Changed in Each Host\n")
                        for i in range(max_length_line+10):
                                print("\033[34m-\033[0m", end = '')
				f.write("-")
			for itm in change_host_list:
				print("\n\033[1;36m%s\033[0m" % (itm))
				f.writelines("\n%s" % (itm))
				for itms in range(len(mt)):
					if mt[itms][0] == itm:
						print("\t\033[1;36m*\033[0m \033[93m%s\033[0m " % (mt[itms][1]))
						f.writelines("\n\t* %s" % (mt[itms][1]))
                        	for i in range(max_length_line+10):
                   	             print("\033[34m-\033[0m", end = '')
				     f.write("-")
			print("\n")
			f.writelines("\n")
		mt1.close()
#########################################################################################################################
	if os.path.exists('comment_temp') == True:
	        ct = open('comment_temp')
		for line in ct:
			command_temp = line
	        os.remove('comment_temp')
	if os.path.exists('report.log') == True:
		rf = open('report.log')
		for line in rf:
			if len(line.strip()) == 0:
				pass
			else:
				host_list.append(line.split(None, 3))
	if os.path.exists('temp_abc') == True:
		fii = open('temp_abc', "r")
	        for line in fii:
                	if len(line.strip()) == 0:
                        	pass
	                else:
				str1, str2, str3 =  line.split(None, 2)
				if str2 == "Unreach":
					stri = str1 + " " + command_temp + " " + str2 + " Host is Unreachable."
				else:
					stri = str1 + " " + command_temp + " " + str2 + " " + str3
                        	host_list.append(stri.split(None, 3))
	if os.path.exists('report.log') == True:
		max_length_line = len(max(open('report.log', 'r'), key=len).strip())
	elif os.path.exists('temp_abc') == True:
		max_length_line = len(max(open('temp_abc', 'r'), key=len).strip())
	if len(host_list) != 0:
		if max_length_line+40 >= 168:
        		max_length_line =128 
		print("\n")
		for i in range(max_length_line+40):
        		print("\033[34m-\033[0m", end = '')
		print("\033[36m\nOutput of Ansible Command\033[0m")
		for i in range(max_length_line+40):
        		print("\033[34m-\033[0m", end ='')
		print("\n\033[1;36mHost Name\033[0m\t\t\t\033[34m|\033[0m\t\033[1;36mCommand Name\033[0m\t\033[34m|\033[0m\033[1;36mStatus\033[0m\033[34m|\033[0m \033[1;36mOutput\033[0m")
		for line in range(len(host_list)):
        		hn,cn,st,outp = host_list[line]
			outp = outp.replace("\\t","  ")
			outp = outp.replace("\\n",",")
			outp = outp.replace("\\r","  ")
			outp = outp.replace("\"","")
			outp = outp.replace("\\\\","\\")
	        	outp = re.sub(r'[\n]', ' ', outp)
			outp = re.sub(' +', ' ', outp)
        		for i in range(max_length_line+40):
                	       print("\033[34m-\033[0m", end='')
			if st.strip() == "Unreach" or st.strip() == "Fail":
	        		print("\n\033[2;93m%s\033[0m\t\t\t\033[34m|\033[0m\t\033[93m%s\033[0m\t\033[34m|\033[0m \033[31m%s\033[0m \033[34m|\033[0m \033[93m%s\033[0m" % ( hn.center(10), cn.center(10), st.center(10).strip(), outp.center(10)))
			else:
		        	print("\n\033[2;93m%s\033[0m\t\t\t\033[34m|\033[0m\t\033[93m%s\033[0m\t\033[34m|\033[0m \033[32m%s\033[0m \033[34m|\033[0m \033[93m%s\033[0m" % ( hn.center(10), cn.center(10), st.center(10).strip(), outp.center(10)))
	        for i in range(max_length_line+40):
        	        print("\033[34m-\033[0m", end ='')
		print("\n")
		if os.path.exists('temp_abc') == True:
			os.remove('temp_abc')
		if os.path.exists('report.log') == True:
			os.remove('report.log')
		if os.path.exists('msg_temp') == True:
		        os.remove('msg_temp')
    def v2_playbook_on_start(self, playbook):
        t17 = threading.Thread(target=print_star, args=("start",))
       	t17.start()
        if self._display.verbosity > 1:
            from os.path import basename
	    f.writelines("%s-----PLAYBOOK: %s\n" % (datetime.now(), basename(playbook._file_name)))

        if self._display.verbosity > 3:
            if self._options is not None:
                for option in dir(self._options):
                    if option.startswith('_') or option in ['read_file', 'ensure_value', 'read_module']:
                        continue
                    val = getattr(self._options, option)
                    if val:
                        self._display.vvvv('%s: %s' % (option, val))
        t17 = threading.Thread(target=print_star, args=("stop",))

    def v2_runner_retry(self, command_result):
        t18 = threading.Thread(target=print_star, args=("",))
       	t18.start()
        task_name = command_result.task_name or command_result._task
        msg = "FAILED - RETRYING: %s (%d retries left)." % (task_name, command_result._result['retries'] - command_result._result['attempts'])
        if (self._display.verbosity > 2 or '_ansible_verbose_always' in command_result._result) and '_ansible_verbose_override' not in command_result._result:
            msg += "Result was: %s" % self._dump_results(command_result._result)
	f.writelines("%s-----%s\n" % (datetime.now(), msg))
        t18 = threading.Thread(target=print_star, args=("stop",))
