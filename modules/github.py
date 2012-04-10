from lib import Command, Event
from mod_data import githubkey
from github2.client import Github
import os, sys, time
import flask

channel = '#urtdevs'
CLI = Github(username="B1narysB0t", api_token=githubkey)
REPOS = [('urtdevs/website', 'master')]
REPOSS = []
app = Flask(__name__)

@app.route("/helo_api/")
def smsEcho():
    print request.args

def init():
    app.run(debug=True, host='0.0.0.0')
    # for pos, i in enumerate(REPOS):
    #     REPOSS.append([CLI.repos.show(i[0])])

# def ready(c):
#     while True:
#         #print 'Looping'
#         for pos, i in enumerate(REPOS):
#             z = CLI.repos.show(i[0])
#             #print z.pushed_at, REPOSS[pos][0].pushed_at
#             if z.pushed_at != REPOSS[pos][0].pushed_at:
#                 REPOSS[pos][0] = z
#                 m = CLI.commits.list(i[0], i[1])
#                 #print 'Sending...'
#                 c.send(channel, 'New commit on %s [%s]: %s (%s)' % (i[0], i[1], m[0].message, 'http://github.com'+m[0].url))
#         time.sleep(30)
