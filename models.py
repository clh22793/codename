import pymongo, datetime, hashlib, base64
from pymongo import MongoClient

# INIT DB CONNECTION
def get_mongo_connection():
    conn = MongoClient('mongodb://aws-us-east-1-portal.14.dblayer.com:10871,aws-us-east-1-portal.13.dblayer.com:10856')
    return conn

def db_connection():
    conn = get_mongo_connection()
    conn['dev-saasdoc'].authenticate('devtest', 'devtest', mechanism='SCRAM-SHA-1')
    return conn['dev-saasdoc']

# simple map function
class Map(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.iteritems():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.iteritems():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]

# DB MODELS ======

class model_base():
    db = db_connection()

    def __init__(self):
        self.set_table()

    def __call__(self, **dict):
        self.query = {}
        for key, val in dict.items():
            self.query[key] = val

        return self

    # DEPRECATED
    def find_one(self, query):
        entity = model_base.db[self.table].find_one(query)
        return entity

    # DEPRECATED
    def insert(self, query):
        uid = model_base.db[self.table].insert_one(query).inserted_id
        entity = self.find_one({"_id": uid})
        return entity

    def query(self, **dict):
        self.query = {}
        for key, val in dict.items():
            self.query[key] = val

        return self

    def get(self):
        entity = model_base.db[self.table].find_one(self.query)

        if entity:
            for key, val in entity.items():
                self.query[key] = val

        return self

    def fetch(self):
        entities = model_base.db[self.table].find(self.query)

        return entities

    def put(self):
        if self.query:
            uid = model_base.db[self.table].insert_one(self.query).inserted_id
            return self

    def __getattr__(self, name):
        if name in self.query:
            return self.query[name]
        else:
            return None

class model_client(model_base):
    def set_table(self):
        self.table = 'clients'

class model_user(model_base):
    def set_table(self):
        self.table = 'users'

class model_oauth(model_base):
    def set_table(self):
        self.table = 'oauth'

class model_api(model_base):
    def set_table(self):
        self.table = 'apis'

class model_swagger(model_base):
    def set_table(self):
        self.table = 'swaggers'

class model_version(model_base):
    def set_table(self):
        self.table = 'versions'

class model_resource(model_base):
    def set_table(self):
        self.table = 'resources'