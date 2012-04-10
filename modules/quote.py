from lib import Cmd, Event, DB, c
from lib import Listener
from database import db
from collections import deque

qz = {}

def getMessage(chan, nick, i=1):
    if chan in qz.keys():
        if nick in qz[chan].keys():
            if len(qz[chan][nick]) >= i-1:
                print qz[chan][nick]
                return qz[chan][nick][-i-1]

@Listener('chansay')
def listener(obj):
    obj.nick = obj.nick.lower()
    if obj.msg.startswith('!'): return
    if obj.chan in qz.keys():
        if obj.nick in qz[obj.chan].keys():
            qz[obj.chan][obj.nick].append(obj)
            if len(qz[obj.chan][obj.nick]) < 30: return
            qz[obj.chan][obj.nick].popleft()
        else:
            qz[obj.chan][obj.nick] = deque()
            listener(obj)
    else:
        qz[obj.chan] = {}
        listener(obj)

@Cmd('!lastmsg', 'See the last message by a user', '%s <user>')
def last(obj):
    msg = obj.msg.split(' ')
    if len(msg) == 2:
        m = getMessage(obj.chan, msg[1])
        if m is None:
            return c.send(obj.chan, 'Error! Oh noez!')
        c.send(obj.chan, '"%s: %s"' % (m.nick, m.msg))
    else:
        c.send(obj.chan, obj.usage)

def save(user, chan, last, test=False):
    if len(msg) == 1:
        
    m = getMessage(chan, nick, last)


@Cmd('!sv', 'Test saving a message to the Quote database', '%s [user] [last count]')
def sv(obj): pass

@Cmd('!save', 'Save the last message in the Quote database', '%s [user] [last count]')
def save(obj):
    msg = obj.msg.split(' ')
    if len(msg) == 1:

def init():
    if not db.hasTable('quotedb'):
        db.addTable('quotedb')
        db['quotedb']['list'] = []
def ready(client): 
    global c
    c = client