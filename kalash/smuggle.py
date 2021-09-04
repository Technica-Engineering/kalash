"""
Adapted from: https://pypi.org/project/smuggle/ with minor changes
related to path handling.
"""
import inspect
import os
import sys
import importlib.util
from typing import Optional


def smuggle(*args, **kwargs):
    """
    Returns the provided soure file as a module.

    Usage:

        weapons = smuggle('weapons.py')
        drugs, alcohol = smuggle('drugs', 'alcohol', source='contraband.py')
    """
    source = kwargs.pop('source', None)

    # Be careful when moving the contents of this
    module_file: Optional[str] = args[0] if len(args) == 1 else source

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

            if len(args) == 1:
                return module

            # Can't use a comprehension here since module wouldn't be in the
            # comprehensions scope for the eval
            returns = []
            for arg in args:
                returns.append(eval('module.{}'.format(arg)))
            return returns
