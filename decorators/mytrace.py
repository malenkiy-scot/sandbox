"""
Count regular (top-level) function calls in another module.

Usage:
   mytrace.trace_module(traced_module1_file_name)
   mytrace.trace_module(traced_module2_file_name)
   
   ...
   
   mytrace.num_calls(module_name, func_name)
"""

__author__ = 'malenkiy_scot'

import inspect

trace_dict = {}


def _do_count(module_name, func_name, func):
    trace_dict[(module_name, func_name)] = 0

    def func_wrapper(*args, **kwargs):
        trace_dict[(module_name, func_name)] += 1
        func(*args, **kwargs)

    return func_wrapper


def trace_module(module_file):
    module_to_trace = __import__(inspect.getmodulename(module_file), globals(), locals(), [], -1)
    for (func_name, func) in inspect.getmembers(module_to_trace, inspect.isfunction):
        setattr(module_to_trace, func_name, _do_count(module_to_trace.__name__, func_name, func))


def num_calls(module_name, func_name):
    try:
        return trace_dict[(module_name, func_name)]
    except KeyError:
        return None
