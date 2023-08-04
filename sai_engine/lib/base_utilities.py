"""
Author: Amith Bhonsle (amith@saisei.com)
Description:
"""
import traceback
import inspect

class BaseUtilities(object):
     '''
     Base class that includes basic functions that is required by every other class
     '''
     def get_function_name(self):
         '''
         This Function return the name of the funtion that is being executed. 
         '''
         return traceback.extract_stack(None, 2)[0][2]

     def get_function_parameters_and_values(self): 
         '''
         This function returns the argments that a function uses. 
         '''
         frame = inspect.currentframe().f_back
         args, _, _, values = inspect.getargvalues(frame)
         return ([(i, values[i]) for i in args])
     