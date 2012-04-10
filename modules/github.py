from lib import Command, Event
from mod_data import githubkey
from github2.client import Github
import os, sys, time
import socket

channel = '#urtdevs'
CLI = Github(username="B1narysB0t", api_token=githubkey)
REPOS = [('urtdevs/website', 'master')]
REPOSS = []


def init():
    for pos, i in enumerate(REPOS):
        REPOSS.append([CLI.repos.show(i[0])])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Please dont jizz in this sock plz ty
    sock.bind(("127.0.0.1", 5050))
    sock.listen(1)
    while True: #Not sure if this will loop even when parsing; inspect later
        client, address = sock.accept()
        data = client.recv(2048) #2048 can be bumped up later, not really a problem
        print data

def ready(c): pass
    # while True:
    #     #print 'Looping'
    #     for pos, i in enumerate(REPOS):
    #         z = CLI.repos.show(i[0])
    #         #print z.pushed_at, REPOSS[pos][0].pushed_at
    #         if z.pushed_at != REPOSS[pos][0].pushed_at:
    #             REPOSS[pos][0] = z
    #             m = CLI.commits.list(i[0], i[1])
    #             #print 'Sending...'
    #             c.send(channel, 'New commit on %s [%s]: %s (%s)' % (i[0], i[1], m[0].message, 'http://github.com'+m[0].url))
    #     time.sleep(15)
