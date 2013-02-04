'''
    xbmcpy.console
    ~~~~~~~~~~~~~~

    This file is part of qobuz-xbmc

    :copyright: (c) 2012 by Joachim Basmaison, Cyril Leclerc
    :license: GPLv3, see LICENSE for more details.
'''
import code
try:
    import readline
except:
    try:
        import pyreadline as readline
    except:
        print "No readline :/"
import atexit
import os

class HistoryConsole(code.InteractiveConsole):

    def __init__(self, locals=None, filename="<console>",
                 histfile=os.path.expanduser("~/.console-history")):
        code.InteractiveConsole.__init__(self, locals, filename)
        self.init_history(histfile)
        self.env_stack = []
        
    def init_history(self, histfile):
        readline.parse_and_bind("tab: complete")
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(histfile)
            except IOError:
                pass
            atexit.register(self.save_history, histfile)

    def save_history(self, histfile):
        readline.write_history_file(histfile)
    
    def get_command(self):
        inp = self.raw_input("\n#> ")
        inpx = inp.split(' ')
        if inpx[0].startswith('help'):
            return ('help', None)
        if inpx[0].startswith('view') and len(inpx) > 1:
            return ('view', int(inpx[1]))
        if inpx[0].startswith('back'):
            return ('back', None)
        return ('nop', None)

    def push_env(self, env):
        if env is None:
            return False
        self.env_stack.insert(0, env)

    def pop_env(self):
        return self.env_stack.pop(0)

console = HistoryConsole()