#==============================================================================
#   Copyright 2014 AlphaOmega Technology
#
#   Licensed under the AlphaOmega Technology Open License Version 1.0
#   You may not use this file except in compliance with this License.
#   You may obtain a copy of the License at
#
#       http://www.alphaomega-technology.com.au/license/AOT-OL/1.0
#==============================================================================
"""
Equation Module
===============

This is the only module you should need to import

It maps the Expression Class from `Equation.core.Expression`

Its recomended you use the code::

    from Equation import Expression
    ...

to import the Expression Class, as this is the only Class/Function you
should use.

.. moduleauthor:: Glen Fletcher <glen.fletcher@alphaomega-technology.com.au>
"""


all = ['util']

try:
    from Equation._info import *
except ImportError:
    from _info import *

try:
    from Equation.core import Expression
except ImportError:
    from core import Expression

def load():
    import os
    import os.path
    import sys
    import traceback
    try:
        import importlib
    except ImportError:
        # Python 2.6 dosen't have importlib used dummy object
        # wrap __import__
        class importlib():
            @staticmethod
            def import_module(name):
                __import__(name)
                return sys.modules[name]
    try:
        from Equation.core import recalculateFMatch
    except ImportError:
        from core import recalculateFMatch
    if not hasattr(load, "loaded"):
        load.loaded = False
    if not load.loaded:
        load.loaded = True
        plugins_loaded = {}
        if __name__ == "__main__":
            dirname = os.path.abspath(os.getcwd())
            prefix = ""
        else:
            dirname = os.path.dirname(os.path.abspath(__file__))
            if __package__ != None:
                prefix = __package__ + "."
            else:
                prefix = ""
        for file in os.listdir(dirname):
            plugin_file,extension = os.path.splitext(os.path.basename(file))
            if not plugin_file.lower().startswith("equation_",0,9) or extension.lower() not in ['.py','.pyc']:
                continue
            if plugin_file not in plugins_loaded:
                plugins_loaded[plugin_file] = 1
                try:
                        plugin_script = importlib.import_module(prefix + plugin_file)
                except:
                        errtype, errinfo, errtrace = sys.exc_info()
                        fulltrace = ''.join(traceback.format_exception(errtype, errinfo, errtrace)[1:])
                        sys.stderr.write("Was unable to load {0:s}: {1:s}\nTraceback:\n{2:s}\n".format(plugin_file, errinfo, fulltrace))
                        continue
                if not hasattr(plugin_script,'equation_extend'):
                    sys.stderr.write("The plugin '{0:s}' from file '{1:s}' is invalid because its missing the attribute 'equation_extend'\n".format(plugin_file,(dirname.rstrip('/') + '/' + plugin_file + extension)))
                    continue
                plugin_script.equation_extend()
        recalculateFMatch()
load()

del load