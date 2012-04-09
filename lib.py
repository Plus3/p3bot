from irc import Connection, Client, Listener
from messages import getString
import time, sys, os, thread, database

AUTO_JOINS = ['plus3']
AUTO_REJOIN = True
SNIDE_MODE = True
CMD_PREFIX = '!'
MODS = ['main']
MODYS = []
THREADS = []
DB = None
c = None

class User():
    def __init__(self, name, host, flags=[False, False]):
        self.name = name
        self.host = host
        self._op = flags[0]
        self._voice = flags[1]
        self.authed = False

    def isAuthed(self): return self.authed
    def isOped(self): return self._op
    def isVoiced(self): return self._voice

class Commandr():
    def __init__(self, cmd, exe, desc, usage, alias):
        self.cmd = cmd
        self.desc = desc
        self.usage = usage
        self.alias = alias
        self.exe = exe

        # for i in self.alias:
        #     alias[i] = cmd

class API():
    events = {}
    commands = {}
    alias = {}

    def fireEvent(self, eve, *data):
        if eve in self.events.keys():
            for i in self.events[eve]:
                thread.start_new_thread(i, data)

    def getUsage(self, orig, ali):
        return self.commands[orig].usage % ali

    def fireCommand(self, cmd, obj):
        print 'Fireing'
        obj.usage = 'Usage: %s' % self.getUsage(cmd, obj.cmd)
        thread.start_new_thread(self.commands[cmd].exe, (obj,))

    def Event(self, events):
        def deco(func):
            for i in events:
                if i not in self.events.keys():
                    self.events[i] = func
                else:
                    self.events[i] += func
            return func
        return deco

def Cmd( cmd, desc, usage, alias=[]):
    global A
    def deco(func):
        A.commands[cmd] = Commandr(cmd, func, desc, usage, alias)
        func.usage = usage
        func.description = desc
        func.command = cmd
        func.rmv = [cmd]+[i for i in alias]
        return func
    return deco
    Command = Cmd

@Listener('command')
def commandListener(arg):
    if arg.cmd in A.commands.keys(): A.fireCommand(arg.cmd, arg)
    elif arg.cmd in A.alias.keys(): A.fireCommand(A.alias[arg.cmd], arg)

A = API()
Command = Cmd

Event = A.Event

def loadMods():
    global MODS, MODYS, THREADS
    for i in MODS:
        __import__('modules.'+i)
        try:
            i = sys.modules['modules.'+i]
            MODYS.append(i)
            THREADS.append(thread.start_new_thread(i.init, ()))
        except Exception, e:
            print 'MODULE ERROR: Please add the function init() to your module.[', e, ']'

def init():
    global DB, CONN, c, AUTO_JOINS, MODYS
    #try:
    if 1==1:
        loadMods()
        DB = database.Database()
        CONN = Connection(Host="gameservers.tx.us.quakenet.org", Nick="PluzB0t").connect(True, debug=False)
        c = Client(CONN)

        for i in MODYS:
            THREADS.append(thread.start_new_thread(i.ready, (c,)))
        
        for chan in AUTO_JOINS:
            c.joinChannel(chan)

        while c.alive:
            c.parse(CONN.read())
    # except Exception, e:
    #     print "Failed to boot: %s" % e
    # finally:
    #     DB.save()

if __name__ == '__main__': init()