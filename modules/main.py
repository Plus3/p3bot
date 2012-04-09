from lib import Cmd, Event, DB
from lib import c
from database import db


@Cmd('!register', 'Register yourself as a user. Use in private messages to the bot /only/', '%s <password (6-35chars)>')
def register(obj):
    print 'BoooooYahhhh'
    msg = obj.msg.split(' ')
    #if not obj.chan == c.nick:
     #   c.send(obj.chan, 'Please register in a private message...')
    if len(msg) == 2: #!register mypass
        if 6 <= len(msg[1]) <= 35: #Is mypass valid?
            if not db.hasUser(obj.nick): #Does the user exist?
                db.addUser(obj.nick).setpass(msg[1]) #Add the user
                return c.send(obj.nick, 'You have been registered with the given password! Login in the future with the !authorize command.')
            else:
                return c.send(obj.chan, 'User already exsists! Please login with !authorize.')
    c.send(obj.chan, obj.usage)      

@Cmd('!setpass', 'Set the password for your user. You must be authed.', '%s <password>')
def setpass(obj):
    msg = obj.msg.split(' ')
    if len(msg) == 2:
        if obj.user.isAuthed():
            obj.user.setpass(msg[1])
            c.send(obj.nick, 'You have reset your password.')
        else:
            c.send(obj.nick, 'Please !authorize before trying to reset your password.')
    else:
        c.send(obj.nick, obj.usage)

@Cmd('!authorize', 'Log yourself into a previously registered account.', '%s [nick] <password>', ['!auth'])
def auth(obj):
    msg = obj.msg.split(' ')
    if len(msg) == 2:
        nick = obj.nick
        pas = msg[1]
    elif len(msg) == 3:
        nick = msg[1]
        pas = msg[2]
    else:
        c.send(obj.nick, obj.usage)

    if db.hasUser(nick):
        if db.getUser(nick).auth(pas):
            obj.user.authed = True
            return c.send(obj.nick, 'Welcome back %s' % nick)
    c.send(obj.nick, 'Incorrect login info!')

@Cmd('!about', 'Get info on the bot and its features.', '%s [feature]', ['!info'])
def about(obj):
    msg = obj.msg.split(' ')
    if len(msg) == 1:
        c.send(obj.chan, 'About topics: Security, Performance')
    elif len(msg) == 2:
        if msg[1].lower() == "security":
            c.send(obj.chan, 'P3-Bot uses a high-level cryptographic framework called "bCrypt" for hashing passwords. \
            Meaning that even if someone was able to obtain a copy of the user database, it could take up to 270+ years \
            to decrypt *ONE* password. All of this is useless if you don\'t use SSL between your client and the IRC server, \
            keep this in mind as you choose a password and use the bot. Passwords are NEVER stored on disk, or in any form unencrypted.')
        elif msg[1].lower() == "performance":
            c.send(obj.chan, 'P3-Bot uses a few cool technologies to improve performance and allow cross-channel high-traffic responses. \
            Every command that the bot parses is threaded, removing a major bottle-neck in other bots.')

@Cmd('!test', 'Test something!','%s')
def test(obj):
    print obj
    print 'Test complete!'

def init(): pass
def ready(client): 
    global c
    print 'Got ready!'
    c = client