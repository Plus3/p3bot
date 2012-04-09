import os, cPickle, bcrypt

class DataUser(object):
    def __init__(self, nick):
        self.nick = nick
        self.hash = None
 
    def auth(self, password):
        if bcrypt.hashpw(password, self.hash) == password: return True
        return False

    def setpass(self, password):
        self.hash = bcrypt.hashpw(password, bcrypt.gensalt(12)) #12 is quite insane. 8 with an 8-char alpha password would take ~246yrs to crack... so uhh... yeah

class Database(object):
    def __init__(self):
        self._data = {}
        self._datafile = None
        if os.path.exists('./data/data.db'):
            try:
                self._datafile = open('./data/data.db', 'rw')
                self._data = cPickle.load(self._datafile)
                return
            except: pass
        self._datafile = open('./data/data.db', 'w').close() #Create file
        self._datafile = open('./data/data.db', 'rw') #Open file for reading/writing
        self._data = {'users':{}}

    def save(self):
        cPickle.dump(self._data, self._datafile)
        self._datafile.close()

    def getUser(self, user):
        return self._data['users'][user]

    def hasTable(self, table):
        if table in self._data.keys(): return True
        return False

    def addTable(self, table, value={}):
        if not self.hasTable(table):
            self._data[table] = value

    def hasUser(self, nick):
        if nick in self._data['users'].keys(): return True
        return False

    def addUser(self, nick):
        nick = nick.lower()
        self._data['users'][nick] = DataUser(nick)
        return db['users'][nick]

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

db = Database()
