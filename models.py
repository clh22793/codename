from pymongo import MongoClient
from ConfigParser import SafeConfigParser
parser = SafeConfigParser()
parser.read("/codename/config")

DB_USERNAME = parser.get('DATABASE', 'USERNAME')
DB_PASSWORD = parser.get('DATABASE', 'PASSWORD')
DB_HOST = parser.get('DATABASE', 'HOST')
DB_NAME = parser.get('DATABASE', 'NAME')

# INIT DB CONNECTION
def get_mongo_connection():
    conn = MongoClient(DB_HOST)
    return conn

def db_connection():
    conn = get_mongo_connection()
    conn[DB_NAME].authenticate(DB_USERNAME, DB_PASSWORD, mechanism='SCRAM-SHA-1')
    return conn[DB_NAME]

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
        self.values = {}
        self.set_table()

    def __call__(self, **dict):
        self.values = {}
        for key, val in dict.items():
            self.values[key] = val

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
        self.values = {}
        for key, val in dict.items():
            self.values[key] = val

        return self

    def get(self, **kwargs):
        query = {}
        for key in kwargs:
            query[key] = kwargs[key]

        entity = model_base.db[self.table].find_one(query)

        print query
        print entity

        if entity:
            return Map(entity)
        else:
            return None

    def fetch(self, **kwargs):
        query = {}
        for key in kwargs:
            query[key] = kwargs[key]

        entities = model_base.db[self.table].find(query)
        return entities

    def insert(self, **kwargs):
        query = {}
        for key in kwargs:
            query[key] = kwargs[key]

        result = model_base.db[self.table].insert_one(query)

        if result.inserted_id:
            return Map(query)
        else:
            return None

    # DEPRECATED
    def put(self, **kwargs):
        query = {}
        for key in kwargs:
            query[key] = kwargs[key]

        id = query['id'] if 'id' in query else None

        result = model_base.db[self.table].replace_one({'id':id}, query, True)

        if result.modified_count == 1:
            return Map(query)
        else:
            return None

    def update(self, **kwargs):
        query = {}
        query["$set"] = {}
        for key in kwargs:
            query["$set"][key] = kwargs[key]

        query["$currentDate"] = {"lastModified":True}

        id = kwargs['id'] if 'id' in kwargs else None

        result = model_base.db[self.table].update_one({'id':id}, query)

        print "UPDATE===="
        print "UPDATING ID: "
        print id
        print "modified_count: "
        print result.modified_count
        print result.raw_result

        if result.modified_count == 1:
            return result
        else:
            return None

    def __getattr__(self, name):
        if name in self.values:
            return self.values[name]
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

class model_endpoint(model_base):
    def set_table(self):
        self.table = 'endpoints'

class model_deployment(model_base):
    def set_table(self):
        self.table = 'deployments'

class model_api_keys(model_base):
    def set_table(self):
        self.table = 'api_keys'

class model_api_objects(model_base):
    def set_table(self):
        self.table = 'api_objects'

