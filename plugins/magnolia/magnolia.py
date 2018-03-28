from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase

class ActionModule(ActionBase):

 def run(self, tmp=None, task_vars=None):
  
  result = super(ActionModule, self).run(tmp, task_vars)
  
  new_module_args = {'name': '@magnolia/cli', 'global': 'yes'}
    
  module_return = self._execute_module(module_name='npm',
                                                 module_args=new_module_args, task_vars=task_vars,
                                                 tmp=tmp)
												 
  result.update(module_return)
  result['msg'] = "Magnolia has been installed."
  return result