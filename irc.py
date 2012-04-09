import socket, thread, random, re
import os, sys, time, thread, time

#LAMBDAZ!
fromHost = lambda host: host.split('!')[0][1:]
modez = {'+':True, '-':False}
hookz = {}
threads = [] #Always keep track of your loose ends! ;)
messgz = {
    'mustbeadmin':'Must be an admin to do that!',
    'botmustbeop':'The bot must be an op to do that!'
}

def Listener(hook):
    def deco(func):
        if hook in hookz: hookz[hook].append(func)
        else: hookz[hook] = [func]
        return func
    return deco

class Data():
    def __init__(self, Type, data):
        self.data = data
        self.type = Type
        self.__dict__.update(data)

def hookFire(hook, data):
    d = Data(hook, data)
    if hook in hookz.keys():
        for i in hookz[hook]:
            threads.append(thread.start_new_thread(i, (d,)))

def niceName(name):
    if name.startswith('@') or name.startswith('+'):
        return name[1:]
    return name

class User():
    def __init__(self, nick, host=None):
        self.nick =  niceName(nick)
        self.hostmask = host
        self.admin = False
        self.aliasis = []

        self.channels = {}
    
    def changeNick(self, newnick):
        self.aliasis.append(self.nick)
        self.nick = newnick

class Penalty():
    def __init__(self, user, reason, byuser, Type):
        self.user = user #user OR hostmask
        self.reason = reason
        self.byuser = byuser
        self.type = Type
        self.time = time.time()
        self.enabled = True

class Channel():
    def __init__(self, name, c):
        self.name = name
        self.c = c
        self.users = {} #(OBJ, VOICE, OP)
        self.topic = ''
        self.modes = {}
        self.penalties = {}

    def op(self, user): self.c.sendRaw('MODE %s +o %s' % (self.name, user)) #once recheckPerms() is implemented, check if user is op

    def deop(self, user): self.c.sendRaw('MODE %s -o %s' % (self.name, user)) #same as above

    def hasUser(self, user):
        if user in self.users: return True
        return False

    def isUserOp(self, user): return self.users[user][2]
    def isUserVoiced(self, user): return self.users[user][1]

    def userNickChanged(self, oldnick, newnick):
        self.users[newnick] = self.users[oldnick]
        del self.users[oldnick]

    def addPenalty(self, user, penalty): pass
        # if user in self.penalties.keys(): self.penalties[user].append(penalty)
        # else: self.penalties[user] = [penalty]

    def userKicked(self, user, byuser, reason): self.addPenalty(user, Penalty(user, reason, byuser, 'kick'))

    def setTopic(self, topic, user): self.topic = topic
    
    def setMode(self, mode, user): self.modes[mode[1:]] = modez[mode[:1]]

    def setUserMode(self, mode, user, byuser): 
        if mode[1:] == 'b' and mode[:1] == '+':
            self.addPenalty(user, Penalty(user, 'None', byuser, 'ban'))
        elif mode[1:] == 'b' and mode[:1] == '-':
            for pen in self.penalties[user]:
                if pen.type is 'ban':
                    pen.enabled = False
        elif mode[1:] == 'v':
            self.users[user][1] = modez[mode[:1]]
        elif mode[1:] == 'o':
            self.users[user][2] = modez[mode[:1]]

    def recheckPerms(self):
        #Eventually pull a user list recheck voice/op
        for i in self.users.values():
            i = i[0]
            if self.name not in i.channels:
                i.channels[self.name] = self

    def updateUsers(self, li):
        for i in li:
            if i not in self.c.users and i not in self.users:
                self.c.users[i] = User(i)
            self.users[i] = [self.c.users[i], False, False]
            self.recheckPerms()
    
    def userPart(self, nick, msg, hostmask):
        print 'User left %s: %s' % (self.name, nick)
        del self.users[nick]

    def userJoin(self, nick, hostmask):
        print 'User joined %s: %s' % (self.name, nick)
        if nick not in self.c.users:
            self.c.users[nick] = User(nick, hostmask)
        self.users[nick] = [self.c.users[nick], False, False]
        self.recheckPerms()
        return self.c.users[nick]

class Connection():
    def __init__(self, Host, Nick, Port=6667):
        self.c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._info = [Host, Port, Nick]

        self.alive = False

    def connect(self, block, debug=False):
        print self._info
        self.c.connect((self._info[0], self._info[1]))
        self.alive = True
        self.c.send('NICK %s\r\n' % self._info[2])
        self.c.send('USER %s 0 * :WittleBoteh Hipstah\r\n' % self._info[2])
        startPong = time.time()
        while time.time()-startPong < 10: #Wait only 10 seconds for a PING message
            x = self.read(out=debug).strip()
            if 'PING' in x:
                self.write('PONG%s' % x.split('PING')[1])
                break
        if block:
            startWait = time.time()
            while time.time() - startWait < 30:
                x = self.read(out=debug).strip()
                if 'End of /MOTD' in x or 'MOTD File is missing':
                    self.write('JOIN #lostchannel')
                    break
        return self

    def disconnect(self):
        self.c.close
        self.alive = False

    def read(self, bytes=4080, out=False): 
        if self.alive is True:
            data = self.c.recv(bytes)
            if data:
                if out: print data
                return data
            else:
                self.disconnect()
        return None

    def write(self, content): self.c.send('%s\r\n' % content)

class Client():
    '''The actual IRC client, wrapped around the Connection class'''
    def __init__(self, connection, rejoin=True):
        self.c = connection
        self.channels = {}
        self.badchannels = []
        self.users = {}
        self.nick = self.c._info[2]
        self.rejoin = rejoin

        self.autoPong = True
        self.botMode = True
        self.botPrefix = '!'
        self.maxLength = 100 #The max length a line can be
        self.printLines = True
        self.alive = True

        self.messages = messgz

    def loop(self):
        while True:
            if self.alive is True:
                self.parse(self.c.read())

    def opUser(self, user, channel=None):
        if channel is None:
            for chan in self.users[user].channels:
                if self.channels[chan].isUserOp(self.nick):
                    self.sendRaw('MODE %s +o %s' % (chan, user)) #use chan.op()
            return True
        else:
            if channel in self.users[user].channels:
                self.sendRaw('MODE %s +o %s' % (channel, user))
                return True
        return False

    def deopUser(self, user, channel=None):
        if channel is None:
            for chan in self.users[user].channels:
                if self.channels[chan].isUserOp(self.nick): #CHANGE THIS TO isClientOp()
                    print self.channels[chan].deop(user)
            return True
        elif channel in self.users[user].channels:
            self.channels[channel].deop(user)
            return True
        return False

    def updateUser(self, user, opts, chan, hosty):
        junks = ['H', 'd', '*'] #Strip out useless chars
        for i in junks:
            opts = opts.strip(i)
        chanob = self.channels[chan]
        if user in self.users.keys():
            userob = self.users[user]
        else:
            userob = chanob.userJoin(user, hosty)
        if user in chanob.users.keys(): #Reset perms
            chanob.users[user][1] = False
            chanob.users[user][2] = False
        if '@' in opts:
            chanob.users[user][2] = True
        if '+' in opts:
            chanob.users[user][1] = True
        
        print user, chanob.isUserOp(user)

    def updateUsers(self, chan=None):
        if chan is None:
            for i in self.channels.keys():
                self.sendRaw('WHO %s' % i)
                #time.sleep(.1) #Do we need to throttle?
        elif chan in self.channels.keys(): #Make sure we're not just WHO'n a random channel
            self.sendRaw('WHO %s' % chan)
    
    def niceList(self, seq, length=None):
        '''Make a nice list!'''
        if not length:
            length = self.maxLength
        ret = [seq[i:i+length] for i in range(0, len(seq), length)]
        return ret

    def quit(self, msg='B1naryth1ef Rocks!'): 
        self.c.write('QUIT :%s' % msg)
        self.c.disconnect()
        self.alive = False
             
    #SEND FUNCTIONS
    def send(self, chan, msg): self.sendRaw('PRIVMSG %s :%s' % (chan, msg))
    def sendRaw(self, raw): self.c.write(raw)
    def sendCTCP(self, user, msg, Type='PRIVMSG'): self.c.write('%s %s :\001%s\001' % (Type, user, msg))
    def inject(self, line): self.parse(line) #Used for testing
    
    #SET FUNCTIONS
    def setUserMode(self, user, channel, mode): pass
    def setChanMode(self, channel, mode): pass
    def setUserAdmin(self, user, stat):
        if user in self.users.keys():
            self.users[user] = stat

    #IF STATEMENTS
    def isClientOp(self, channel): return self.channels[channel].users[self.nick][2]
    def isClientVoiced(self, channel): return self.channels[channel].users[self.nick][1]
    def isClientAdmin(self, nick):
        if nick in self.users.keys():
            if self.users[nick].admin is True:
                return True
        return False
    def isClientInChannel(self, channel):
        if channel in self.channels.keys():
            return True
        return False

    def joinChannel(self, channel, passwd=''):
        if not channel.startswith('#'): channel = '#'+channel
        if not self.isClientInChannel(channel):
            self.c.write('JOIN %s %s' % (channel, passwd))
            self.updateUsers(channel)
            self.channels[channel] = Channel(channel, self)
    
    def partChannel(self, channel, msg='G\'bye!'):
        if self.isClientInChannel(channel):
            self.c.write('PART %s :%s' % (channel, msg))
            del self.channels[channel]

    def niceParse(self):
        self.parse(self.c.read())
    
    def makeAdmin(self, nick):
        if nick in self.users.keys():
            self.users[nick].admin = True
            return True
        return False

    def removeAdmin(self, nick):
        if nick in self.users.keys():
            self.users[nick].admin = False
            return True
        return False

    def sendMustBeAdmin(self, chan):
        self.send(chan, self.messages['mustbeadmin'])   
    def sendClientMustBeOp(self, chan):
        self.send(chan, self.messages['botmustbeop'])

    def parse(self, inp):
        def names(msg):
            try:
                msg = msg.split(':', 2)
                chan = msg[1].split(' ')[4]
                users = msg[2].split(' ')
                names = []
                for i in users:
                    names.append(niceName(i))
                self.channels[chan].updateUsers(names)
                hookFire('names', {'nicks':names, 'chan':chan})
            except Exception, e:
                print 'Error parsing NAMES line: %s' % e

        def topic(msg):
            msg = msg.split(':', 2)
            chan = msg[1].split(' ')[3]
            topic = msg[2]
            self.channels[chan].setTopic(topic, '*')
            hookFire('topic', {'chan':chan, 'topic':topic})
        
        def part(msg):
            msg = msg.split(' ')
            hostmask = msg[0]
            chan = msg[2]
            if len(msg) == 4: pmsg = msg[3][1:]
            else: pmsg = None
            nick = fromHost(hostmask)
            if nick != self.nick:
                self.channels[chan].userPart(nick, pmsg, hostmask)
                hookFire('part', {'hostmask':hostmask, 'nick':nick, 'msg':pmsg, 'chan':chan})

        def join(msg):
            msg = msg.split(' ')
            hostmask = msg[0]
            chan = msg[2]
            nick = fromHost(hostmask)   
            if chan in self.channels.keys():
                self.channels[chan].userJoin(nick, hostmask)
            if nick == self.nick:
                if chan not in self.channels.keys():
                    print 'Adding %s' % chan
                    self.channels[chan] = Channel(chan, self)
            hookFire('join', {'hostmask':hostmask, 'chan':chan, 'nick':nick})
        
        def mode(msg):
            msg = msg.split(' ')
            hostmask = msg[0]
            chan = msg[2]
            fromuser = fromHost(hostmask)
            if msg[2] == self.nick: pass
            elif len(msg) == 4: #Channel Mode
                mode = msg[3]
                if fromuser != mode:
                    self.channels[chan].setMode(mode, fromuser)
                    hookFire('channelmode', {'hostmask':hostmask, 'fromnick':fromuser, 'mode':mode})
            elif len(msg) >= 5: #User Mode
                touser = niceName(msg[4])
                mode = msg[3]
                self.channels[chan].setUserMode(mode, touser, fromuser)
                hookFire('usermode', {'fromnick':fromuser, 'tonick':touser, 'mode':mode, 'chan':chan})

        def settopic(msg):
            msg = msg.split(' ', 3)
            hostmask = msg[0]
            chan = msg[2]
            newtopic = msg[3][1:]
            nick = fromHost(hostmask)
            self.channels[chan].setTopic(newtopic, nick)
            hookFire('settopic', {'hostmask':hostmask, 'nick':nick, 'newtopic':newtopic})
        
        def msg(msg):
            msg = msg.split(' ', 3)
            hostmask = msg[0]
            chan = msg[2]
            msg = msg[3][1:]
            nick = fromHost(hostmask)
            print '[%s] %s: %s' % (chan, nick, msg)
            if chan == self.nick:
                chan = nick
                hookFire('privsay', {'hostmask':hostmask, 'nick':nick, 'msg':msg, 'chan':chan})
            else:
                hookFire('chansay', {'hostmask':hostmask, 'nick':nick, 'msg':msg, 'chan':chan})
            if self.botMode is True and msg.startswith(self.botPrefix):
                hookFire('command', {'hostmask':hostmask, 'nick':nick, 'msg':msg, 'chan':chan, 'cmd':msg.split(' ')[0]})
        
        def kick(msg):
            msg = msg.split(' ')
            hostmask = msg[0]
            chan = msg[2]
            fromnick = fromHost(hostmask)
            nick = niceName(msg[3])
            reason = msg[4][1:]
            if reason == nick:
                reason = 'none given'
            if self.nick == nick:
                hookFire('uskicked', {'chan':chan, 'fromnick':fromnick})
                del self.channels[chan]
                if self.rejoin is True:
                    self.joinChannel(chan)
            else:
                self.channels[chan].userKicked(nick, fromnick, reason)
                hookFire('kick', {'fromnick':fromnick, 'nick':nick, 'chan':chan, 'reason':reason})

        def nick(msg):
            msg = msg.split(' ')
            hostmask = msg[0]
            fromnick = fromHost(hostmask)
            tonick = niceName(msg[2][1:])
            for chan in self.channels.values():
                if chan.hasUser(fromnick):
                    chan.userNickChanged(fromnick, tonick)
            try:
                self.users[tonick] = self.users[fromnick]
                del self.users[fromnick]
            except Exception, e:
                print e
            hookFire('nick_change', {'hostmask':hostmask, 'fromnick':fromnick, 'tonick':tonick})

        def who(line):
            '''/WHO Response'''
            msg = line.split(' ')
            if len(msg) >= 9:
                name = msg[4].strip('~')
                hostmask = msg[5]
                nick = niceName(msg[7])
                opts = msg[8]
                chan = msg[3]
                try:
                    self.updateUser(nick, opts, chan, hostmask)
                except Exception, e:
                    print 'Problem parsing WHO line: %s' % e
                hookFire('who_response', {'name':name, 'hostmask':hostmask, 'nick':nick, 'opts':opts})

        def pong(line):
            '''Server ping request'''
            if self.autoPong is True: self.c.write('PONG')
            hookFire('ping', {'line':line})

        def ctcp(orig, line):
            '''CTCP request'''
            line = line.split(' ')
            sender = fromHost(line[0])
            hookFire('ctcp', {'line':line, 'nick':sender})
            if line[3] == ':\x01PING':
                timey = str(time.time()).split('.')
                self.sendCTCP(sender, 'PING %s %s' % (timey[0], timey[1]), 'NOTICE')

        if inp != None:
            inp = inp.split('\r\n')
        else:
            return

        for l in inp:
            if self.printLines is True and l not in [None, '', '\r\n']: print '[X]',l
            line_type = l.strip().split(' ')
            line = l.strip()
            orig = l
            if '\001' in orig: ctcp(orig, line)
            if len(line_type) >= 2:
                print '>>>>',line_type[1]
                if line_type[1] == 'PRIVMSG': msg(line)
                elif line_type[0] == 'PING': pong(line)
                elif line_type[1] == '353': names(line)
                elif line_type[1] == '332': topic(line)
                elif line_type[1] == '352': who(line)
                elif line_type[1] == 'PART': part(line)
                elif line_type[1] == 'JOIN': join(line)
                elif line_type[1] == 'MODE': mode(line)
                elif line_type[1] == 'TOPIC': settopic(line)
                elif line_type[1] == 'KICK': kick(line)
                elif line_type[1] == 'NICK': nick(line)
            
