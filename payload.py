#from webapp2_extras import json
#import time
import json

class ParameterPayload:
    def __init__(self, name, parameters):
        self.setParameters(name, parameters)

    def getPayload(self, json_encode=True):
        if json_encode:
            return json.dumps(self.payload)
        else:
            return self.payload

class Payload:
    def __init__(self, model):
        self.setPayload(model)

    def getPayload(self, json_encode=True):
        if json_encode:
            return json.dumps(self.payload)
        else:
            return self.payload

class UsersPayload(Payload):
    def setPayload(self, model):
        self.payload = {'meta': {'type':'user', 'created':str(model.created)}, 'content': {'id':model.user_id, 'username':model.username}}

class OauthPayload(Payload):
    def setPayload(self, model):
        self.payload = {'meta':{'type':'oauth'}, 'content':{"user_id" :model.user_id, "access_token":model.access_token, "refresh_token":model.refresh_token}}

class ApiPayload(Payload):
    def setPayload(self, model):
        self.payload = {'meta':{'type':'api'}, 'content':{"id" :model.id, "title":model.title, "created":str(model.created)}}

class VersionPayload(Payload):
    def setPayload(self, model):
        self.payload = {'meta':{'type':'version'}, 'content':{"id" :model.id, "name":model.name, "base_url":model.base_url}}

class SaasdocPayload(Payload):
    def setPayload(self, model):
        self.payload = {'meta':{'type':'saasdoc'}, 'content':{"id" :model.saasdoc_id, "name":model.name, "public":model.public,
                                                              "created":str(model.created), "confirmed":model.confirmed, "logo_url":model.logo_url,
                                                              "homepage_url": model.homepage_url, "company":model.company, "med_logo_url":model.med_logo_url,
                                                              "logo_height":model.logo_height, "logo_offset":(80 - model.logo_height) / 2,
                                                              "start_tour":model.start_tour, "apiname":model.apiname}}



class SectionPayload(Payload):
    def setPayload(self, model):
        self.payload = {'meta':{'type':'section'}, 'content':{"id" :model.section_id, "name":model.name, "content": model.content, "version_id":model.version_id}}

# DEPRECATED
class EndpointPayload(Payload):
    def setPayload(self, model):
        self.payload = {'meta':{'type':'endpoint'}, 'content':{"id" :model.endpoint_id, "relative_url":model.relative_url, "title":model.title,
                                                               "http_method": model.http_method, "header_params":model.header_params,
                                                               "body_params":model.body_params, "query_params":model.query_params,
                                                               "sample_response":model.sample_response, "response_content_type":model.response_content_type,
                                                               "description":model.description, "response_http_code":model.response_http_code,
                                                               "example_request":model.example_request, "request_content_type":model.request_content_type,
                                                               "resourcegroup_id":model.resourcegroup_id, "priority":model.priority, "version":model.version_id,
                                                               "resourcegroup":model.resource_group, "python_code":model.python_code,
                                                               "curl_code":model.curl_code, "php_code":model.php_code, "node_code":model.node_code,
                                                               "java_code":model.java_code}}

class ResourcePayload(Payload):
    def setPayload(self, model):
        self.payload = {'meta':{'type':'resource'}, 'content':{"id" :model.resource_id, "name":model.name, "version_id":model.version_id,
                                                               "description":model.description, "plurality":model.plurality, "relates_to":model.relates_to,
                                                               "auth_method":model.auth_method, "fields":model.fields}}

class ResourceEndpointPayload(Payload):
    def setPayload(self, model):
        self.payload = {'meta':{'type':'endpoint'}, 'content':{"id" :model.endpoint_id, "resource_id":model.resource_id, "http_method":model.http_method,
                                                               "har_request":model.har_request, "response":model.response, "curl_code":model.curl_code,
                                                               "python_code":model.python_code, "php_code": model.php_code, "node_code":model.node_code,
                                                               "java_code":model.java_code,
                                                               "excluded_params":model.excluded_params, "auth_method":model.auth_method,
                                                               "collection":model.collection, "request_content_type":model.request_content_type,
                                                               "version_id":model.version_id, "name":model.name, "relative_url":model.relative_url}}

class AppClientPayload(Payload):
    def setPayload(self, model):
        self.payload = {'meta':{'type':'appclient'}, 'content':{"id":model.appclient_id, "client_id":model.client_id, "client_secret":model.client_secret}}

class AppUserPayload(ParameterPayload):
    def setParameters(self, name, parameters):
        content = {}
        for key, value in parameters.iteritems():
            content[key] = value

        self.payload = {'meta':{'type':name}, 'content':content}

class AppResourcePayload(ParameterPayload):
    def setParameters(self, name, parameters):
        content = {}
        for key, value in parameters.iteritems():
            content[key] = value

        self.payload = {'meta':{'type':name}, 'content':content}
