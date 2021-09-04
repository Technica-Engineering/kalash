"""
Adapted from: https://pypi.org/project/smuggle/ with minor changes
related to path handling.
"""
import inspect
import os
import sys
import importlib.util
from types import ModuleType


def smuggle(module_file: str) -> ModuleType:
    """
    Loads an arbitrary Python file as a module.

    Args:
        module_file (str): path to
            the file containing the module to be loaded

    Returns:
        `ModuleType`
    """

    if module_file:
        module_name = os.path.splitext(os.path.basename(module_file))[0]

        if os.path.isabs(module_file):
            abs_path = module_file
        else:
            directory = os.path.dirname(inspect.stack()[1][1])
            abs_path = os.path.normpath(os.path.join(directory, module_file))

        sys.path.append(os.path.dirname(abs_path))
        sys.path.append(os.getcwd())
        spec = importlib.util.spec_from_file_location(module_name, abs_path)
        if spec:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            if spec.loader:
                exec_module = getattr(spec.loader, 'exec_module')
                exec_module(module)

            return module

    raise NameError("Module could not be loaded! Check if the path is correct")
