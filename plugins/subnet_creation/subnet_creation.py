from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible.module_utils.parsing.convert_bool import boolean

class ActionModule(ActionBase):

 def run(self, tmp=None, task_vars=None):
  
  result = super(ActionModule, self).run(tmp, task_vars)
  cidr = self._task.args.get('cidr', None)
  cidr = cidr.replace(" ", "")
  cidr_block = cidr.split(",")
  
  resource_tags_list = self._task.args.get('resource_tags', {})
  resource_tags_list = resource_tags_list['Name']
  resource_tags_list = resource_tags_list.replace(" ", "")
  resource_tags_list = resource_tags_list.split(",")
    
  new_module_args = self._task.args.copy() 
  new_resource_tags = self._task.args.get('resource_tags', {})
  result_array = []
  
  for block, item in zip(cidr_block, resource_tags_list):
   new_resource_tags['Name']=item
   new_module_args.update(
                    dict(
                        cidr=block,
						resource_tags=new_resource_tags
                    ),
                )
   module_return = self._execute_module(module_name='ec2_vpc_subnet', module_args=new_module_args, task_vars=task_vars, tmp=tmp)
   if module_return.get('failed'):
                result.update(failed=True, module_return=module_return)
                return result
   else:
    result_array.append(module_return)
   
  result.update(dict(result_array=result_array))
  return result