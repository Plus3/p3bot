import random

msgs = {
'part':[
'See you bitches later!',
'Peace!',
'I WILL BE BACK! MWHAHAHAHHAH'],

'rejoin_on_kick':[
'Jeeze %s is a tight-wad...',
'%s: Boticus 13:4 "Thou shall not kick a Boteth"',
'%s: bring it...',
'%s: its on gurlllll!',
'%s: try me!'],
}

def getString(field):
    return random.choice(msgs[field])