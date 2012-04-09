from lib import Command, Event
from moddata import githubkey, repos
from github2.client import Github

REPOS = []
CLIENT = Github(username="B1narysB0t", api_token=githubkey)
[('b1naryth1ef/japil', 'master'), 'b1naryth1ef/pydskchk', 'master']


def init():
    for i in repos:
        r = Repo(i[0])
        #r.create_remote('origin', i[2])
        o = r.remotes.origin
        o.pull()
        REPOS.append(o)
    while True:
        time.sleep(30)
        for i in REPOS:
            i.pull()

