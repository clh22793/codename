from flask import Flask, json, request, make_response
import json,datetime,base64

# internal imports
import customexception
from util import Util
from verifyrequest import VerifyRequest
from payload import UsersPayload
from payload import OauthPayload
from payload import ApiPayload
from payload import VersionPayload
from payload import SwaggerPayload
from models import model_user
from models import model_oauth
from models import model_api
from models import model_swagger
from models import model_client
from models import model_version

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

    def process(self, request, resource_id=None):
        self.authorize(request)

        if request.method == 'POST':
            return self.post(request, resource_id)
        elif request.method == 'GET':
            return self.get(request, resource_id)
        elif request.method == 'PUT':
            return self.put(request, resource_id)
        elif request.method == 'DELETE':
            return self.delete(request, resource_id)

class BearerRequestHandler(RequestHandler):
    def authorize(self, request):
        # Authorization
        self.oauth = VerifyRequest.authorization('bearer', request)

class BasicRequestHandler(RequestHandler):
    def authorize(self, request):
        # Authorization
        self.client = VerifyRequest.authorization('basic', request)

class ClientHandler(BasicRequestHandler):
    def post(self, request):
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

class UserHandler(BearerRequestHandler):
    def post(self, request):
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
    def post(self, request):
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

            oauth = self.Oauths(access_token=access_token, refresh_token=refresh_token, created=created, active=active, user_id=user_id)
            oauth.put()

            response = make_response(OauthPayload(oauth).getPayload(), 201)
        else:
            raise customexception.AuthException(customexception.invalid_user_creds)

        return response

class ApiHandler(BearerRequestHandler):
    def post(self, request, *argv):
        data = json.loads(request.get_data())
        title = data['title']
        created = datetime.datetime.utcnow()
        active = True

        api = self.Apis.query(title=title, active=True).get()
        if not api._id:
            api = self.Apis(id=Util.generate_id(title+self.oauth.user_id), title=title, created=created, active=active, user_id=self.oauth.user_id)
            api.put()

            response = make_response(ApiPayload(api).getPayload(), 201)
            #return response

        else:
            raise customexception.ResourceException(customexception.api_already_exists)

        #response = make_response(ApiPayload(api).getPayload(), 201)

        return response

class VersionHandler(BearerRequestHandler):
    def post(self, request, *argv):
        api_id = argv[0]

        data = json.loads(request.get_data())
        name = data['name']
        created = datetime.datetime.utcnow()
        active = True
        #id = Util.generate_id(name+self.oauth.user_id)

        version = self.Versions.query(name=name, api_id=api_id, active=True).get()
        if not version._id:
            version = self.Versions(id=name, name=name, api_id=api_id, created=created, active=active, user_id=self.oauth.user_id)
            version.put()

            response = make_response(VersionPayload(version).getPayload(), 201)
            #return response

        else:
            raise customexception.ResourceException(customexception.version_already_exists)

        #response = make_response(VersionPayload(version).getPayload(), 201)

        return response

class SwaggerHandler(BearerRequestHandler):
    def post(self, request, *argv):
        api_id = argv[0]

        data = json.loads(request.get_data())
        name = data['name']
        created = datetime.datetime.utcnow()
        active = True
        #id = Util.generate_id(name+self.oauth.user_id)

        swagger = self.Swaggers.query(name=name, api_id=api_id, active=True).get()
        if not swagger._id:
            swagger = self.Versions(id=name, name=name, api_id=api_id, created=created, active=active, user_id=self.oauth.user_id)
            swagger.put()

            response = make_response(SwaggerPayload(swagger).getPayload(), 201)

        else:
            raise customexception.ResourceException(customexception.swagger_already_exists)

        return response