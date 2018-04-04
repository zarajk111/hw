#!/usr/bin/env python

import os
import time
import argparse
import subprocess
import glob
import json
from   shutil    import copy2, copytree


__DESCRIPTION__='''
=========================================
           # RerunTestList #
=========================================
This class is used to rerun tests from specific tests list files
which stored in JSON format. Normal usecase is reruning failed tests
in regressions from file 'failed_test_list.json', which is generated 
in run_report.py script and will be automaticly called by run_plan.py
script. You can also specify user-defined test lists and multiple test
lists are also supported, but must keep the same format as shown in 
'failed_test_list.json' file.
'''

class  RerunTestList(object):

    def __init__(self, test_list, lsf_cmd):
        self._test_list = test_list
        self._lsf_cmd   = lsf_cmd
        self._test_db   = {}

    def run(self):
        self.load_test_db()
        cmd_file = self.gen_rerun_cmd()
        self.execute_rerun_cmd(cmd_file)

    def load_test_db(self):
        for item in self._test_list:
            with open(item, 'r') as fh:
                db = json.load(fh)
                self._test_db.update(db) #TBD: multiple list may exist same key

    def gen_rerun_cmd(self):
        cmd_file = []
        for idx,info in self._test_db.items():
            rerun_dir = info['dir']+'.rerun'
            os.makedirs(rerun_dir, exist_ok=True)
            #copytree(os.path.join(info['dir'],info['name']), rerun_dir)
            for sh_file in  glob.glob(info['dir']+'/*.sh'):
                copy2(sh_file, rerun_dir)
            cmd_file.append(os.path.join(rerun_dir, 'run_trace_player.sh'))
        return cmd_file
            

    def execute_rerun_cmd(self, cmd_file):
        origin_working_dir = os.getcwd()
        for item in cmd_file:
            rerun_dir = os.path.dirname(item)
            os.chdir(rerun_dir)
            cmd = ' '.join([self._lsf_cmd, item])
            print('[RERUN]: execute command \" %0s \"' % cmd)
            subprocess.Popen(cmd, shell=True)
            time.sleep(1)
        time.sleep(10)
        os.chdir(origin_working_dir)




def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=__DESCRIPTION__)
    parser.add_argument('--test_list','-test_list', dest='test_list', required=True, default=[], type=str, nargs='+',
                        help='provide rerun test list, which should be generated by run_report.py')
    parser.add_argument('--lsf_command', '-lsf_command', '--lsf_cmd', '-lsf_cmd', dest='lsf_cmd', required=False, default='',
                        help='LSF command to run tests')
    config = vars(parser.parse_args())
    rerun_test_list = RerunTestList(test_list = config['test_list'],
                                  lsf_cmd   = config['lsf_cmd'],
                                 )
    rerun_test_list.run()
    # TBD: add run_report function if needed

if __name__ == '__main__':
    main()
