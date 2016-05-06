from flask import Flask, json, request, make_response
from werkzeug import secure_filename
import json,datetime,base64,os

# internal imports
import customexception
from util import Util
from verifyrequest import VerifyRequest
from payload import UsersPayload
from payload import OauthPayload
from payload import ApiPayload
from payload import VersionPayload
from payload import ResourcePayload
from payload import SwaggerPayload

from models import Map

from models import model_user
from models import model_oauth
from models import model_api
from models import model_swagger
from models import model_client
from models import model_version
from models import model_resource


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

    #def process(self, request, resource_id=None):
    def process(self, **kwargs):
        self.authorize(kwargs['request'])

        print kwargs

        if request.method == 'POST':
            return self.post(**kwargs)
        elif request.method == 'GET':
            return self.get(**kwargs)
        elif request.method == 'PUT':
            return self.put(**kwargs)
        elif request.method == 'DELETE':
            return self.delete(**kwargs)

class BearerRequestHandler(RequestHandler):
    def authorize(self, request):
        # Authorization
        self.oauth = VerifyRequest.authorization('bearer', request)

class BasicRequestHandler(RequestHandler):
    def authorize(self, request):
        # Authorization
        self.client = VerifyRequest.authorization('basic', request)

class ClientHandler(BasicRequestHandler):
    def post(self, **kwargs):
        request = kwargs['request']

        email = request.form['email']
        client_secret = request.form['client_secret']
        client_id = request.form['client_id']
        token = base64.b64encode(client_id+':'+client_secret)
        active = True
        created = datetime.datetime.utcnow()

        # insert unique record
        client = self.Clients.query(email=email).get()
        if not client._id:
            client = self.Clients(email=email, client_id=client_id, client_secret=client_secret, token=token, active=active, created=created)
            client.put()

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
        active = True
        created = datetime.datetime.utcnow()
        user_id= Util.generate_token('user'+username+password)

        user = self.Users.query(username=username, active=True).get()
        if not user._id:
            user = self.Users(username=username, user_id=user_id, password=password, active=active, created=created)
            user.put()

            response = make_response(UsersPayload(user).getPayload(), 201)
            return response

        else:
            raise customexception.ResourceException(customexception.user_already_exists)

class OauthHandler(BasicRequestHandler):
    def post(self, **kwargs):
        request = kwargs['request']

        # check for user
        username = request.form['username']
        password = request.form['password']
        user = self.Users.query(username=username, password=Util.generate_password(password)).get()

        if user.user_id:
            # create token
            access_token = Util.generate_token('access_token'+username+password)
            refresh_token = Util.generate_token('access_token'+username+password)
            created = datetime.datetime.utcnow()
            active = True
            user_id = user.user_id

            oauth = self.Oauths(access_token=access_token, refresh_token=refresh_token, created=created, active=active, user_id=user_id, client_id=self.client.id)
            oauth.put()

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

        api = self.Apis.query(title=title, active=True).get()
        if not api._id:
            api = self.Apis(id=Util.generate_id(title+self.oauth.user_id), title=title, created=created, active=active, user_id=self.oauth.user_id, client_id=self.oauth.client_id)
            api.put()

            response = make_response(ApiPayload(api).getPayload(), 201)
        else:
            raise customexception.ResourceException(customexception.api_already_exists)

        return response

    def get(self, **kwargs):
        api_id = kwargs['api_id'] if 'api_id' in kwargs else None

        if api_id:
            api = self.Apis.query(user_id=self.oauth.user_id, id=api_id, active=True).get()
            response = make_response(ApiPayload(api).getPayload(), 200)
        else:
            apis = self.Apis.query(user_id=self.oauth.user_id, active=True).fetch()

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

        data = json.loads(request.get_data())
        name = data['name']
        created = datetime.datetime.utcnow()
        active = True
        #id = Util.generate_id(name+self.oauth.user_id)

        version = self.Versions.query(name=name, api_id=api_id, active=True).get()
        if not version._id:
            version = self.Versions(id=Util.generate_id(name+api_id), name=name, api_id=api_id, created=created, active=active, user_id=self.oauth.user_id, client_id=self.oauth.client_id)
            version.put()

            response = make_response(VersionPayload(version).getPayload(), 201)
            #return response

        else:
            raise customexception.ResourceException(customexception.version_already_exists)

        #response = make_response(VersionPayload(version).getPayload(), 201)

        return response

    def get(self, **kwargs):
        api_id = kwargs['api_id'] if 'api_id' in kwargs else None

        versions = self.Versions.query(user_id=self.oauth.user_id, api_id=api_id, active=True).fetch()

        versions_payload = []

        for version in versions:
            tmp = Map(version)
            versions_payload.append(VersionPayload(tmp).getPayload(False))

        response = make_response(json.dumps(versions_payload), 200)

        return response

class ResourceHandler(BearerRequestHandler):
    def post(self, **kwargs):
        request = kwargs['request']
        version_id = kwargs['version_id'] if 'version_id' in kwargs else None

        data = json.loads(request.get_data())
        name = data['name']
        plurality = data['plurality']
        parent = data['parent']
        parameters = data['parameters']
        created = datetime.datetime.utcnow()
        active = True
        #id = Util.generate_id(name+self.oauth.user_id)

        resource = self.Resources.query(name=name, version_id=version_id, active=True).get()
        if not resource._id:
            resource = self.Resources(id=Util.generate_id(name), name=name, version_id=version_id, plurality=plurality, parent=parent, parameters=parameters, created=created, active=active, user_id=self.oauth.user_id, client_id=self.oauth.client_id)
            resource.put()

            response = make_response(ResourcePayload(resource).getPayload(), 201)
            #return response

        else:
            raise customexception.ResourceException(customexception.resource_already_exists)

        #response = make_response(VersionPayload(version).getPayload(), 201)

        return response

    def get(self, **kwargs):
        version_id = kwargs['version_id'] if 'version_id' in kwargs else None
        resource_id = kwargs['resource_id'] if 'resource_id' in kwargs else None

        if version_id:
            resources = self.Resources.query(user_id=self.oauth.user_id, version_id=version_id, active=True).fetch()

            resources_payload = []

            for resource in resources:
                tmp = Map(resource)
                resources_payload.append(ResourcePayload(tmp).getPayload(False))

            response = make_response(json.dumps(resources_payload), 200)

        elif resource_id:
            resource = self.Resources.query(user_id=self.oauth.user_id, id=resource_id, active=True).get()
            response = make_response(ResourcePayload(resource).getPayload(), 200)


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
