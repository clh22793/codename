import json, requests
import hashlib, time, random, re, base64
import customexception
from ConfigParser import SafeConfigParser
parser = SafeConfigParser()
parser.read("/codename/config")

class Util:
    @staticmethod
    def generate_hash(value, algorithm):
        if algorithm == 'sha1':
            hash_object = hashlib.sha1(value)
        elif algorithm == 'sha256':
            hash_object = hashlib.sha256(value)
        elif algorithm == 'md5':
            hash_object = hashlib.md5(value)

        return hash_object.hexdigest()

    @staticmethod
    def generate_id(value):
        hash_object = hashlib.sha1(value+str(time.time())+str(random.random()))
        return hash_object.hexdigest()

    # DEPRECATED
    @staticmethod
    def generate_token(value):
        hash_object = hashlib.sha1(value+str(time.time())+str(random.random()))
        return hash_object.hexdigest()

    @staticmethod
    def generate_password(value):
        hash_object = hashlib.sha256(value)
        return hash_object.hexdigest()

    @staticmethod
    def generate_client_credential(value):
        hash_object = hashlib.md5(value+str(time.time())+str(random.random()))
        return hash_object.hexdigest()

    @staticmethod
    def generate_temporary_username():
        return str(random.random())

    # DEPRECATED
    @staticmethod
    def create_oauth_record(access_token, refresh_token, user):
        oauth = OauthRec()
        oauth.access_token = access_token
        oauth.refresh_token = refresh_token
        oauth.user_id = user.user_id
        oauth.key = ndb.Key('OauthRec', Util.generate_token('oauth'+access_token+refresh_token), parent=ndb.Key(user.key.kind(), user.key.id()))
        oauth.put()
        return oauth

    # DEPRECATED
    @staticmethod
    def create_version(name, saasdoc):
        version = Version(parent = saasdoc.key, name = name, version_id = Util.generate_token('version'+name), saasdoc_id = saasdoc.saasdoc_id)
        version.put()
        return version

    # DEPRECATED
    @staticmethod
    def create_section(name, version, content, order):
        section = Section(parent = version.key, name = name, order=order, content=content, section_id = Util.generate_token('section'+name), saasdoc_id=version.saasdoc_id, version_id=version.version_id)
        section.put()
        return section

    @staticmethod
    def generate_example_request(base_url, params):
        return "curl "+base_url+params['relative_url']+\
               Util.get_query_params(params)+\
               Util.get_header_params(params)+\
               Util.get_body_params(params)+\
               Util.get_file_params(params)

    @staticmethod
    def get_query_params(params):
        query_params = []

        for query_param in params['query_params']:
            query_params.append(query_param['name']+"=["+query_param['name'].upper()+"]")

        if not query_params:
            return ""
        else:
            return "?"+"&".join(query_params)

    @staticmethod
    def get_header_params(params):
        header_params = []

        for header_param in params['header_params']:
            header_params.append("\n-H \""+header_param['name']+":["+header_param['name'].upper()+"]\"")

        if len(header_params) == 0:
            return ""
        else:
            return " "+" ".join(header_params)

    @staticmethod
    def get_body_params(params):
        if params['request_content_type'] == 'application/x-www-form-urlencoded':
            body_params=[]
            for param in params['body_params']:
                body_params.append(param['name']+"="+param['name'].upper())

            if len(body_params) == 0:
                return ""
            else:
                return " --data \""+"&".join(body_params)+"\""

        else:
            body_params={}
            for param in params['body_params']:
                body_params[param['name']] = param['name'].upper()

            if len(body_params) == 0:
                return ""
            else:
                return " --data '"+json.encode(body_params)+"'"

    @staticmethod
    def get_file_params(params):
        if params['request_content_type'] == 'multipart/form-data':
            return " -F 'file=@FILE_PATH'"
        else:
            return ""

    @staticmethod
    def get_resource_group_name(relative_url):
        matches = re.finditer(r'\/[a-zA-Z0-9]+', relative_url)

        for match in matches:
            tmp = match.group()

        if tmp:
            return tmp[1:].capitalize()
        else:
            return None

    @staticmethod
    def get_endpoint_priority(http_method):
        if http_method.lower() == 'post':
            return 100
        elif http_method.lower() == 'get':
            return 200
        elif http_method.lower() == 'put':
            return 300
        elif http_method.lower() == 'delete':
            return 400
        else:
            return 500

    @staticmethod
    # proper slashing prefix
    def sanitize_relative_url(relative_url):
        if relative_url[0] == "/":
            return relative_url
        elif relative_url[0] == "\\" :
            relative_url = relative_url[1:]

        return "/"+relative_url

    @staticmethod
    def generate_gravatar_url(email):
        hash_object = hashlib.md5(email)
        hash =  hash_object.hexdigest()

        return "https://secure.gravatar.com/avatar/"+hash

    @staticmethod
    # this generates a medium size logo per cloudinary spec
    def generate_med_logo_url(logo_url):
        return logo_url.replace("/upload/", "/upload/c_scale,w_200/")

    @staticmethod
    # body_param['type'], body_param['value']; determine and return the correct type of 'value'
    def translate_body_param_value(body_param):
        if body_param['type'].lower() == 'number':
            try:
                return int(body_param['value'])
            except:
                return float(body_param['value'])
        else:
            return body_param['value']

    @staticmethod
    def get_basic_auth_parameters(request):
        # handle basic auth
        match = re.search(r'(\-u|\-\-user) +[a-zA-Z0-9\-_]+:([ a-zA-Z0-9\-_]+)?', request)
        if match:
            match = re.search(r'[a-zA-Z0-9\-_]+:([ a-zA-Z0-9\-_]+)?', match.group())
            if match:
                parts = match.group().split(':')

                return {'user':parts[0], 'pass':parts[1]}

        return None

    # DEPRECATED
    @staticmethod
    def get_har_request(params, http_method, base_url=None):
        request = {}
        request['method'] = http_method.lower()

        # get request url
        request['url'] = base_url + params['relative_url']

        # get header params
        if 'header_params' in params:
            for param in params['header_params']:
                if 'headers' not in request:
                    request['headers'] = []

                request['headers'].append({"name":param['name'], "value":param['value']})

        '''
        # get -u | --user basic auth shorthand
        match = re.search(r'(\-u|\-\-user) +[a-zA-Z0-9\-_]+:([a-zA-Z0-9\-_]+)?', params['example_request'])
        if match:
            auth = match.group()
            parts = auth.split()
            if 'headers' not in request:
                request['headers'] = []
            request['headers'].append({"name":"Authorization", "value":"basic "+base64.b64encode(parts[1])})
        '''

        # get querystring
        if 'query_params' in params:
            for param in params['query_params']:
                if 'queryString' not in request:
                    request['queryString'] = []

                request['queryString'].append({"name":param['name'], "value":param['value']})

        # get posted params
        json_body = {}

        if 'body_params' in params:
            #print "BODY_PARAMS"
            #print params['body_params']

            for param in params['body_params']:
                if 'postData' not in request:
                    request['postData'] = {"mimeType":params['request_content_type'], "params":[], "text":""}
                    #request['postData'] = {"mimeType":params['mimeType'], "params":[], "text":""}

                if params['request_content_type'] == 'application/json':
                    #request['postData']['text'].append(json.encode({"key":"value", "price":100.5}))
                    #print "IF"
                    #print param
                    '''
                    if param['type'] == 'number':
                        value = int(param['value'])
                    elif param['type'] == 'boolean' and param['value'].lower() == 'true':
                        value = True
                    elif param['type'] == 'boolean' and param['value'].lower() == 'false':
                        value = False
                    else:
                        value = param['value']
                    '''

                    json_body[param['name']] = Util.get_typed_value(param['value'], param['type'])
                elif params['request_content_type'] == 'application/x-www-form-urlencoded':
                    request['postData']['params'].append({"name":param['name'], "value":param['value']})
                elif params['request_content_type'] == 'multipart/form-data':
                    request['postData']['params'].append({"name":param['name'], "value":param['value']})

        if json_body:
            request['postData']['text'] = json.encode(json_body)

        return request

    @staticmethod
    def get_typed_value(value, type):
        if type.lower() == 'number':
            value = int(value)
        elif type.lower() == 'boolean' and value.lower() == 'true':
            value = True
        elif type.lower() == 'boolean' and value.lower() == 'false':
            value = False
        else:
            value = value

        return value

    @staticmethod
    def get_code_snippets(har_request):
        response = requests.post('http://45.55.47.103/har', json.dumps(har_request))

        return response.json()

    @staticmethod
    def get_auth_token(type, request):
        auth_header = request.headers['Authorization']
        parts = auth_header.split(' ')
        token = parts[1]

        if type == 'basic' and parts[0].lower() == 'basic':
            return token
        elif type == 'bearer' and parts[0].lower() == 'bearer':
            return token
        else:
            raise customexception.AuthException(customexception.invalid_token_type)

    @staticmethod
    def replace_non_alnum_chars(string, replace_with=''):
        return re.sub(r'[^a-zA-Z0-9]',replace_with, string)

    @staticmethod
    def get_relative_url(method, resource, collection, parent_resource=None):
        if method.lower() == 'get' and collection == True and parent_resource:
            relative_url = parent_resource.plurality.lower()+"/{"+parent_resource.name.upper()+"_ID}/"+resource.plurality.lower()
        elif method.lower() == 'get' and collection == True:
            relative_url = resource.plurality.lower()
        elif method.lower() == 'get':
            relative_url = resource.plurality.lower()+"/{"+resource.name.upper()+"_ID}"
        elif method.lower() == 'post' and parent_resource is None:
            relative_url = resource.plurality.lower()
        elif method.lower() == 'post':
            relative_url = parent_resource.plurality.lower()+"/{"+parent_resource.name.upper()+"_ID}/"+resource.plurality.lower()
        elif method.lower() == 'put':
            relative_url = resource.plurality.lower()+"/{"+resource.name.upper()+"_ID}"
        else:
            relative_url = resource.plurality.lower()+"/{"+resource.name.upper()+"_ID}"

        return relative_url

    @staticmethod
    def generate_har_request(method, resource, version, relative_url, base_url):
        headers = []

        if resource.auth_type == 'basic':
            headers.append({"name":"Authorization", "value":"Basic [MAGICSTACK_TOKEN]"})
        else: # == 'oauth2'
            headers.append({"name":"Authorization", "value":"Bearer [ACCESS_TOKEN]"})

        queryString = []
        postData = {"mimeType":"application/json", "params":[], "text":""}

        if method.lower() == 'post' or method.lower() == 'put':
            data_json = {}
            for parameter in resource.parameters:
                print "parameter"
                print parameter
                if parameter['read_only'] == False:
                    if parameter['type'].lower() == 'string':
                        test_value = "test value"
                    elif parameter['type'].lower() == 'number':
                        test_value = 101
                    elif parameter['type'].lower() == 'boolean':
                        test_value = True
                    elif parameter['type'].lower() == 'object':
                        test_value = {}
                    else: #elif parameter['type'].lower() == 'array':
                        test_value = []

                    data_json[parameter['name']] = test_value
                    #postData['params'].append({"name":parameter['name'], "value":"test value"})

            postData['text'] = json.dumps(data_json)

            headers.append({"name":"Content-Type", "value":"application/json"})

        url = base_url + version.name + '/' + relative_url

        har_request = {"method":method, "url":url, "headers":headers, "queryString":queryString, "postData":postData}

        return har_request

    @staticmethod
    def get_base_url():
        '''
        env = Util.get_environment()
        if env == 'dev':
            return 'http://dev.magicstack.io/'
        else:
            return 'http://prod.magicstack.io/'
        '''

        return parser.get('GENERAL', 'MAGIC_BASE_URL')


    @staticmethod
    def get_environment():
        return parser.get('GENERAL', 'ENVIRONMENT')
