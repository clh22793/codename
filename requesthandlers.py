from flask import Flask, json, request, make_response
from werkzeug import secure_filename
import json,datetime,base64,os, uuid
import mailgun
from ConfigParser import SafeConfigParser
parser = SafeConfigParser()
parser.read("config")

# internal imports
import customexception
from util import Util
from swagger import Swagger
from verifyrequest import VerifyRequest
from payload import UsersPayload
from payload import OauthPayload
from payload import ApiPayload
from payload import VersionPayload
from payload import ResourcePayload
from payload import EndpointPayload
from payload import SwaggerPayload
from payload import DeploymentPayload
from payload import ApiKeysPayload

from models import Map

from models import model_user
from models import model_oauth
from models import model_api
from models import model_swagger
from models import model_client
from models import model_version
from models import model_resource
from models import model_endpoint
from models import model_deployment
from models import model_api_keys
from models import model_api_objects


class RequestHandler():
    def __init__(self):
        self.init()

    def init(self):
        self.Apis = model_api()
        self.Users= model_user()
        self.Oauths = model_oauth()
        self.Swaggers = model_swagger()
        self.Clients = model_client()
        self.Versions = model_version()
        self.Resources = model_resource()
        self.Endpoints = model_endpoint()
        self.Deployments = model_deployment()
        self.Api_keys = model_api_keys()
        self.Api_objects = model_api_objects()

    def process(self, **kwargs):
        self.authorize(kwargs['request'])
        return self.route_method(**kwargs)

    def route_method(self, **kwargs):
        if request.method == 'POST':
            return self.post(**kwargs)
        elif request.method == 'GET':
            return self.get(**kwargs)
        elif request.method == 'PUT':
            return self.put(**kwargs)
        elif request.method == 'DELETE':
            return self.delete(**kwargs)

    def save_endpoint(self, data, resource_id):

        method = data['method']
        name = data['name']
        collection = data['collection'] if 'collection' in data else False
        created = datetime.datetime.utcnow()
        active = True
        #resource_id = resource.id

        resource = self.Resources.get({"id":resource_id, "active":True})
        endpoint = self.Endpoints.get({"method":method, "resource_id":resource_id, "collection":collection, "active":True})
        version = self.Versions.get({"id":resource.version_id, "active":True})

        if endpoint:
            self.Endpoints.update(id=endpoint.id, active=False)

        parent_resource = self.Resources.get({"id":resource.parent_resource_id, "active":True}) if resource.parent_resource_id else None
        relative_url = Util.get_relative_url(method, resource, collection, parent_resource)
        har_request = Util.generate_har_request(method, resource, version, relative_url, Util.get_base_url())
        code_snippets = Util.get_code_snippets(har_request)
        code_snippets['curl'] = code_snippets['curl'].replace('%7B', ':').replace('%7D', '');

        consumes = []
        produces = []
        if method.lower() == 'post' or method.lower() == 'put':
            consumes.append('application/json')
            produces.append('application/json')
        elif method.lower() == 'get':
            produces.append('application/json')

        # create acp
        acp = {"owner":{"type":"user", "id":self.oauth.user_id}, "access_control_list":[{"type":"user", "id":self.oauth.user_id, "permissions":["read", "write"]}]}

        endpoint = self.Endpoints.insert(id=Util.generate_id(method), version_id=resource.version_id, relative_url=relative_url,
                                         code_snippets=code_snippets, method=method, collection=collection, har_request=har_request,
                                         name=name, resource_id=resource_id, created=created, active=active, user_id=self.oauth.user_id,
                                         client_id=self.oauth.client_id, produces=produces, consumes=consumes, access_control_policy=acp)

        return endpoint

    def save_deployment(self, version_id, magic_environment):
        active = True
        created = datetime.datetime.utcnow()

        # insert deployment object
        resources = self.Resources.fetch({"version_id":version_id, "active":True})
        tmp_resources = []
        for resource in resources:
            tmp_resources.append(Map(resource))
        resources = tmp_resources

        endpoints = self.Endpoints.fetch({"version_id":version_id, "active":True})
        tmp_endpoints = []
        for endpoint in endpoints:
            tmp_endpoints.append(Map(endpoint))
        endpoints = tmp_endpoints

        version = self.Versions.get({"id":version_id, "active":True})
        api = self.Apis.get({"id":version.api_id, "active":True})

        swagger_object = Swagger.generate(api, version, resources, endpoints, magic_environment)

        # create acp
        acp = {"owner":{"type":"user", "id":self.oauth.user_id}, "access_control_list":[{"type":"user", "id":self.oauth.user_id, "permissions":["read", "write"]}]}

        deployment = self.Deployments.insert(id=Util.generate_id(version_id), version_id=version_id, version_name=version.name, api_id=api.id, swagger=swagger_object, environment=magic_environment, created=created, active=active, user_id=self.oauth.user_id, client_id=self.oauth.client_id, access_control_policy=acp)

        return deployment

class BearerRequestHandler(RequestHandler):
    def authorize(self, request):
        # Authorization
        self.oauth = VerifyRequest.authorization('bearer', request)

class BasicRequestHandler(RequestHandler):
    def authorize(self, request):
        # Authorization
        self.client = VerifyRequest.authorization('basic', request)

class ClientHandler(RequestHandler):
    def process(self, **kwargs):
        return self.route_method(**kwargs)

    def post(self, **kwargs):
        request = kwargs['request']

        email = request.form['email']
        client_secret = request.form['client_secret']
        client_id = request.form['client_id']
        token = base64.b64encode(client_id+':'+client_secret)
        active = True
        created = datetime.datetime.utcnow()

        # insert unique record
        client = self.Clients.get({"email":email})
        if not client:
            client = self.Clients.insert(email=email, client_id=client_id, client_secret=client_secret, token=token, active=active, created=created)

            response = make_response('client created', 201)

        else:
            response = make_response('client not created', 200)

        return response

class UserHandler(BasicRequestHandler):
    def post(self, **kwargs):
        request = kwargs['request']

        # get vars
        username = request.form['username']
        password = Util.generate_password(request.form['password'])
        name = request.form['name']
        active = True
        created = datetime.datetime.utcnow()
        user_id= Util.generate_token('user'+username+password)

        user = self.Users.get({"username":username, "active":True})
        if not user:
            acp = {"owner":{"type":"client", "id":self.client.client_id}, "access_control_list":[{"type":"client", "id":self.client.client_id, "permissions":["read", "write"]}]}

            user = self.Users.insert(username=username, id=user_id, password=password, name=name, active=active, created=created, access_control_policy=acp)
            response = make_response(UsersPayload(user).getPayload(), 201)

            # send welcome email
            email_client = mailgun.Email(parser.get('GENERAL', 'ENVIRONMENT'))
            email_client.send_welcome_message(username)

            return response

        else:
            raise customexception.ResourceException(customexception.user_already_exists)

class OauthHandler(BasicRequestHandler):
    def post(self, **kwargs):
        request = kwargs['request']

        # check for user
        username = request.form['username']
        password = request.form['password']
        user = self.Users.get({"username":username})

        #Util.confirm_password(password, user.password)

        #if user:
        if user and Util.confirm_password(password, user.password):
            # create token
            access_token = Util.generate_token('access_token'+username+password)
            refresh_token = Util.generate_token('access_token'+username+password)
            created = datetime.datetime.utcnow()
            active = True
            user_id = user.id

            # create acp
            acp = {"owner":{"type":"client", "id":self.client.client_id}, "access_control_list":[{"type":"client", "id":self.client.client_id, "permissions":["read", "write"]}]}

            oauth = self.Oauths.insert(id=Util.generate_id(access_token), access_token=access_token, refresh_token=refresh_token, created=created, active=active, user_id=user_id, client_id=self.client.client_id, access_control_policy=acp)

            response = make_response(OauthPayload(oauth).getPayload(), 201)
        else:
            raise customexception.AuthException(customexception.invalid_user_creds)

        return response

class ApiHandler(BearerRequestHandler):
    def post(self, **kwargs):
        request = kwargs['request']

        data = json.loads(request.get_data())
        title = data['title']
        created = datetime.datetime.utcnow()
        active = True

        #api = self.Apis.get({"title":title, "user_id":self.oauth.user_id, "active":True})
        api = self.Apis.get({"title":title, "client_id":self.oauth.client_id, "active":True})
        if not api:
            # create acp
            acp = {"owner":{"type":"user", "id":self.oauth.user_id}, "access_control_list":[{"type":"user", "id":self.oauth.user_id, "permissions":["read", "write"]}]}

            # create api
            api_id = Util.generate_id(title+self.oauth.user_id)
            api = self.Apis.insert(id=api_id, title=title, created=created, active=active, user_id=self.oauth.user_id, client_id=self.oauth.client_id, access_control_policy=acp)

            # create 1st api key
            u1 = uuid.uuid4()
            u2 = uuid.uuid4()
            api_client_id = Util.generate_hash('client_id'+title+str(u1.int), 'md5') #  Util.generate_id('client_id'+title)
            api_client_secret = Util.generate_hash('client_secret'+title+str(u2.int), 'md5') # Util.generate_id('client_secret'+title)
            basic_key = base64.b64encode(api_client_id+":"+api_client_secret)
            api_key = self.Api_keys.insert(id=Util.generate_id(api_client_id+api_client_secret), user_id=self.oauth.user_id, api_id=api_id, active=active, client_id=api_client_id, client_secret=api_client_secret, basic_key=basic_key, created=created, access_control_policy=acp)

            response = make_response(ApiPayload(api).getPayload(), 201)
        else:
            raise customexception.ResourceException(customexception.api_already_exists)

        return response

    def get(self, **kwargs):
        api_id = kwargs['api_id'] if 'api_id' in kwargs else None

        if api_id:
            #api = self.Apis.get(user_id=self.oauth.user_id, id=api_id, active=True)
            api = self.Apis.get({"user_id":self.oauth.user_id, "id":api_id, "active":True, "access_control_policy.access_control_list.id": self.oauth.user_id, "access_control_policy.access_control_list.permissions":"read"})
            response = make_response(ApiPayload(api).getPayload(), 200)
        else:
            apis = self.Apis.fetch({"user_id":self.oauth.user_id, "active":True, "access_control_policy.access_control_list.id": self.oauth.user_id, "access_control_policy.access_control_list.permissions": "read"})

            apis_payload = []

            for api in apis:
                tmp = Map(api)
                apis_payload.append(ApiPayload(tmp).getPayload(False))

            response = make_response(json.dumps(apis_payload), 200)

        return response


class VersionHandler(BearerRequestHandler):
    def post(self, **kwargs):
        #api_id = argv[0]
        request = kwargs['request']
        api_id = kwargs['api_id'] if 'api_id' in kwargs else None

        # check acp for api_id
        api_acp = self.Apis.get({"id":api_id, "active":True, "access_control_policy.access_control_list.id": self.oauth.user_id, "access_control_policy.access_control_list.permissions": "write"})
        if not api_acp:
            raise customexception.ResourceException(customexception.permission_denied)

        data = json.loads(request.get_data())
        name = data['name']
        created = datetime.datetime.utcnow()
        active = True
        version_id = Util.generate_id(name+api_id)
        #id = Util.generate_id(name+self.oauth.user_id)

        version = self.Versions.get({"name":name, "api_id":api_id, "active":True})

        print "\n\nPOST VERSION============\n\n\n"

        if not version:
            # create acp
            acp = {"owner":{"type":"user", "id":self.oauth.user_id}, "access_control_list":[{"type":"user", "id":self.oauth.user_id, "permissions":["read", "write"]}]}

            print "\n\ninserting version with acp==================\n\n"


            version = self.Versions.insert(id=version_id, name=name, api_id=api_id, created=created, active=active, user_id=self.oauth.user_id, client_id=self.oauth.client_id, access_control_policy=acp)
            print version
            print "\n\n"


            # create default user resource
            parameters = []
            parameters.append({"name":"username", "description":"email address", "read_only":False, "required":True, "type":"String", "fixed":True})
            parameters.append({"name":"password", "description":"user password", "read_only":False, "required":True, "type":"String", "fixed":True})
            resource = self.Resources.insert(id=Util.generate_id('user'), template='user', name='user', auth_type='basic', version_id=version_id, plurality='users', parent_resource_id='None', parameters=parameters, created=created, active=active, user_id=self.oauth.user_id, client_id=self.oauth.client_id, access_control_policy=acp)
            # end default user resource

            # create default user endpoints
            self.save_endpoint({"name":"Add a "+resource.name, "method":"post","collection":False}, resource.id)
            self.save_endpoint({"name":"Get a "+resource.name, "method":"get","collection":False}, resource.id)
            self.save_endpoint({"name":"Get a collection of "+resource.name, "method":"get","collection":True}, resource.id)
            self.save_endpoint({"name":"Update a "+resource.name, "method":"put","collection":False}, resource.id)
            self.save_endpoint({"name":"Delete a "+resource.name, "method":"delete","collection":False}, resource.id)
            # end user endpoints

            # create default deployment
            magic_environment = "prod" # prod || sandbox
            self.save_deployment(version_id, magic_environment)
            # end create deployment

            response = make_response(VersionPayload(version).getPayload(), 201)

        else:
            raise customexception.ResourceException(customexception.version_already_exists)

        #response = make_response(VersionPayload(version).getPayload(), 201)

        return response

    def get(self, **kwargs):
        api_id = kwargs['api_id'] if 'api_id' in kwargs else None

        #versions = self.Versions.fetch(user_id=self.oauth.user_id, api_id=api_id, active=True)
        versions = self.Versions.fetch({"user_id":self.oauth.user_id, "api_id":api_id, "active":True, "access_control_policy.access_control_list.id": self.oauth.user_id, "access_control_policy.access_control_list.permissions": "read"})

        versions_payload = []

        for version in versions:
            tmp = Map(version)
            versions_payload.append(VersionPayload(tmp).getPayload(False))

        response = make_response(json.dumps(versions_payload), 200)

        return response

class ResourceHandler(BearerRequestHandler):
    def sanitize_parameters(self, parameters):
        pass

    def post(self, **kwargs):
        request = kwargs['request']
        version_id = kwargs['version_id'] if 'version_id' in kwargs else None

        # check acp for version_id
        version_acp = self.Versions.get({"id":version_id, "active":True, "access_control_policy.access_control_list.id": self.oauth.user_id, "access_control_policy.access_control_list.permissions": "write"})
        if not version_acp:
            raise customexception.ResourceException(customexception.permission_denied)

        data = json.loads(request.get_data())
        name = data['name'].lower()
        plurality = data['plurality'].lower()
        parent_resource_id = data['parent_resource_id'] if 'parent_resource_id' in data else None
        parameters = data['parameters'] if 'parameters' in data else None
        # sanitize parameters
        for param in parameters:
            param['name'] = param['name'].replace("__","_")

            if param['name'][0:1] == "_":
                param['name'] = param['name'].replace("_","",1)

            param['name'] = param['name'].strip().replace(' ', '_')


        created = datetime.datetime.utcnow()
        resource_id = Util.generate_id(name)
        template = data['template'].lower()
        auth_type = 'oauth2'
        active = True

        resource = self.Resources.get({"name":name, "version_id":version_id, "active":True})
        if not resource:
            # create acp
            acp = {"owner":{"type":"user", "id":self.oauth.user_id}, "access_control_list":[{"type":"user", "id":self.oauth.user_id, "permissions":["read", "write"]}]}

            resource = self.Resources.insert(id=resource_id, template=template, auth_type=auth_type, name=name, version_id=version_id, plurality=plurality, parent_resource_id=parent_resource_id, parameters=parameters, created=created, active=active, user_id=self.oauth.user_id, client_id=self.oauth.client_id, access_control_policy=acp)

            response = make_response(ResourcePayload(resource).getPayload(), 201)

        else:
            raise customexception.ResourceException(customexception.resource_already_exists)

        return response

    def get(self, **kwargs):
        version_id = kwargs['version_id'] if 'version_id' in kwargs else None
        resource_id = kwargs['resource_id'] if 'resource_id' in kwargs else None

        if version_id:
            #resources = self.Resources.fetch(user_id=self.oauth.user_id, version_id=version_id, active=True)
            resources = self.Resources.fetch({"version_id":version_id, "active":True, "access_control_policy.access_control_list.id": self.oauth.user_id, "access_control_policy.access_control_list.permissions": "read"})

            resources_payload = []

            for resource in resources:
                tmp = Map(resource)
                resources_payload.append(ResourcePayload(tmp).getPayload(False))

            response = make_response(json.dumps(resources_payload), 200)

        else: # resource_id
            resource = self.Resources.get({"id":resource_id, "active":True, "access_control_policy.access_control_list.id": self.oauth.user_id, "access_control_policy.access_control_list.permissions": "read"})

            response = make_response(ResourcePayload(resource).getPayload(), 200)

        return response

    def put(self, **kwargs):
        resource_id = kwargs['resource_id'] if 'resource_id' in kwargs else None

        # check acp for resource_id
        resource_acp = self.Resources.get({"id":resource_id, "active":True, "access_control_policy.access_control_list.id": self.oauth.user_id, "access_control_policy.access_control_list.permissions": "write"})
        if not resource_acp:
            raise customexception.ResourceException(customexception.permission_denied)

        data = json.loads(request.get_data())
        name = data['name'].lower()
        plurality = data['plurality'].lower()
        parent_resource_id = data['parent_resource_id'] if 'parent_resource_id' in data else None
        parameters = data['parameters'] if 'parameters' in data else None
        # sanitize parameters
        for param in parameters:
            param['name'] = param['name'].strip().replace(' ', '_')

        resource = self.Resources.update(id=resource_id, name=name, plurality=plurality, parent_resource_id=parent_resource_id, parameters=parameters)

        if resource:
            resource = self.Resources.get({"id":resource_id})

            response = make_response(ResourcePayload(resource).getPayload(), 200)

            return response

    def delete(self, **kwargs):
        resource_id = kwargs['resource_id'] if 'resource_id' in kwargs else None

        # check acp for resource_id
        resource_acp = self.Resources.get({"id":resource_id, "active":True, "access_control_policy.access_control_list.id": self.oauth.user_id, "access_control_policy.access_control_list.permissions": "write"})
        if not resource_acp:
            raise customexception.ResourceException(customexception.permission_denied)

        resource = self.Resources.get({"id":resource_id, "active":True})
        if resource.template.lower() == "user":
            raise customexception.ResourceException(customexception.cannot_delete_resource)

        # first, raise error if there are any children of this resource
        children = self.Resources.fetch({"parent_resource_id":resource_id, "active":True})
        print "CHILDREN======="

        if children.count() > 0:
            raise customexception.ResourceException(customexception.resource_has_children)

        # delete resource
        resource = self.Resources.update(id=resource_id, active=False)

        # delete resource endpoints
        endpoints = self.Endpoints.fetch({"resource_id":resource_id, "active":True})

        for endpoint in endpoints:
            tmp = Map(endpoint)
            print "TMP"
            print tmp
            #endpoints_payload.append(EndpointPayload(tmp).getPayload(False))
            self.Endpoints.update(id=tmp.id, active=False)

        # create deployment
        #magic_environment = "prod" # prod || sandbox
        #self.save_deployment(resource.version_id, magic_environment)
        # end create deployment

        # return empty response
        response = make_response(json.dumps({}), 200)
        return response


class EndpointHandler(BearerRequestHandler):
    def post(self, **kwargs):
        request = kwargs['request']
        resource_id = kwargs['resource_id'] if 'resource_id' in kwargs else None

        # check acp for resource_id
        resource_acp = self.Resources.get({"id":resource_id, "active":True, "access_control_policy.access_control_list.id": self.oauth.user_id, "access_control_policy.access_control_list.permissions": "write"})
        if not resource_acp:
            raise customexception.ResourceException(customexception.permission_denied)

        data = json.loads(request.get_data())

        method = data['method']
        name = data['name']
        collection = data['collection'] if 'collection' in data else False
        created = datetime.datetime.utcnow()
        active = True

        print "ENDPOINT HANDLER================="
        print data
        endpoint = self.save_endpoint(data, resource_id)
        '''
        resource = self.Resources.get(id=resource_id, active=True)
        endpoint = self.Endpoints.get(method=method, resource_id=resource_id, collection=collection, active=True)
        version = self.Versions.get(id=resource.version_id, active=True)

        if endpoint:
            self.Endpoints.update(id=endpoint.id, active=False)

        parent_resource = self.Resources.get(id=resource.parent_resource_id, active=True) if resource.parent_resource_id else None
        relative_url = Util.get_relative_url(method, resource, collection, parent_resource)
        har_request = Util.generate_har_request(method, resource, version, relative_url, Util.get_base_url())
        code_snippets = Util.get_code_snippets(har_request)
        code_snippets['curl'] = code_snippets['curl'].replace('%7B', ':').replace('%7D', '');

        consumes = []
        produces = []
        if method.lower() == 'post' or method.lower() == 'put':
            consumes.append('application/json')
            produces.append('application/json')
        elif method.lower() == 'get':
            produces.append('application/json')

        endpoint = self.Endpoints.insert(id=Util.generate_id(method), version_id=resource.version_id, relative_url=relative_url,
                                         code_snippets=code_snippets, method=method, collection=collection, har_request=har_request,
                                         name=name, resource_id=resource_id, created=created, active=active, user_id=self.oauth.user_id,
                                         client_id=self.oauth.client_id, produces=produces, consumes=consumes)
        '''

        response = make_response(EndpointPayload(endpoint).getPayload(), 201)

        return response

    def get(self, **kwargs):
        request = kwargs['request']
        resource_id = kwargs['resource_id'] if 'resource_id' in kwargs else None

        #endpoints = self.Endpoints.fetch(resource_id=resource_id, active=True)
        endpoints = self.Endpoints.fetch({"resource_id":resource_id, "active":True, "access_control_policy.access_control_list.id": self.oauth.user_id, "access_control_policy.access_control_list.permissions": "read"})

        endpoints_payload = []

        for endpoint in endpoints:
            tmp = Map(endpoint)
            endpoints_payload.append(EndpointPayload(tmp).getPayload(False))

        response = make_response(json.dumps(endpoints_payload), 200)

        return response

class DeploymentHandler(BearerRequestHandler):
    def post(self, **kwargs):
        request = kwargs['request']
        version_id = kwargs['version_id'] if 'version_id' in kwargs else None

        # check acp for version_id
        version_acp = self.Versions.get({"id":version_id, "active":True, "access_control_policy.access_control_list.id": self.oauth.user_id, "access_control_policy.access_control_list.permissions": "write"})
        if not version_acp:
            raise customexception.ResourceException(customexception.permission_denied)

        data = json.loads(request.get_data())

        magic_environment = data['environment'] # prod || sandbox
        created = datetime.datetime.utcnow()
        active = True

        # update all existing deployments to active=False
        deployments = self.Deployments.fetch({"version_id":version_id, "environment":magic_environment})
        for deployment in deployments:
            self.Deployments.update(id=deployment['id'], active=False)

        # insert deployment object
        '''
        resources = self.Resources.fetch(version_id=version_id, active=True)
        tmp_resources = []
        for resource in resources:
            tmp_resources.append(Map(resource))
        resources = tmp_resources

        endpoints = self.Endpoints.fetch(version_id=version_id, active=True)
        tmp_endpoints = []
        for endpoint in endpoints:
            tmp_endpoints.append(Map(endpoint))
        endpoints = tmp_endpoints

        version = self.Versions.get(id=version_id, active=True)
        api = self.Apis.get(id=version.api_id, active=True)

        swagger_object = Swagger.generate(api, version, resources, endpoints, magic_environment)
        deployment = self.Deployments.insert(id=Util.generate_id(version_id), version_id=version_id, version_name=version.name, api_id=api.id, swagger=swagger_object, environment=magic_environment, created=created, active=active, user_id=self.oauth.user_id, client_id=self.oauth.client_id)
        '''

        deployment = self.save_deployment(version_id, magic_environment)

        response = make_response(DeploymentPayload(deployment).getPayload(), 201)

        return response

class ApiKeysHandler(BearerRequestHandler):
    def get(self, **kwargs):
        request = kwargs['request']
        api_id = kwargs['api_id'] if 'api_id' in kwargs else None

        print "api_id: "+api_id
        print "user_id: "+self.oauth.user_id

        #settings = self.Settings.fetch(api_id=api_id, user_id=self.oauth.user_id, active=True)
        api_keys = self.Api_keys.get({"user_id":self.oauth.user_id, "api_id":api_id, "active":True})

        print "api_keys:"
        print api_keys

        response = make_response(ApiKeysPayload(api_keys).getPayload(), 200)

        return response

class DataHandler(BearerRequestHandler):
    def get(self, **kwargs):
        request = kwargs['request']
        resource_id = kwargs['resource_id'] if 'resource_id' in kwargs else None

        # check acp for resource_id
        resource = self.Resources.get({"id":resource_id, "active":True, "access_control_policy.access_control_list.id": self.oauth.user_id, "access_control_policy.access_control_list.permissions": "read"})
        if not resource:
            raise customexception.ResourceException(customexception.permission_denied)

        print "resource!!!"
        print resource

        # get api_objects with this resource_id
        api_objects = self.Api_objects.fetch({"resource_id":resource['id'], "active":True})

        data_payload = []

        for api_object in api_objects:
            if resource.template == "user":
                print "API_OBJECT===="
                print api_object
                api_object['body']['content'].pop('password',None)

            data_payload.append(api_object['body'])

        response = make_response(json.dumps(data_payload), 200)

        return response

class SwaggerHandler(BearerRequestHandler):
    ALLOWED_EXTENSIONS = set(['json'])
    UPLOAD_FOLDER = 'uploads'

    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1] in SwaggerHandler.ALLOWED_EXTENSIONS

    def post(self, **kwargs):
        request = kwargs['request']
        version_id = kwargs['version_id'] if 'version_id' in kwargs else None

        file = request.files['file']
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            content = file.read()
            file.save(os.path.join(SwaggerHandler.UPLOAD_FOLDER, filename))

            id = Util.generate_id(self.oauth.user_id+filename)
            created = datetime.datetime.utcnow()
            active = True

            version = self.Versions.query(id=version_id).get()

            swagger = self.Swaggers(id=id, api_id=version.api_id, version_id=version.id, created=created, active=active, user_id=self.oauth.user_id, content=content, client_id=self.oauth.client_id)
            swagger.put()

            response = make_response(SwaggerPayload(swagger).getPayload(), 201)

        else:
            response = make_response('ERROR: File not uploaded', 200)

        return response
