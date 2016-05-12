from models import model_api
from models import model_version
from models import model_resource
from models import model_endpoint
import json

class Swagger:
    @staticmethod
    def generate(api, version, resources, endpoints, environment):
        swagger_object = {}
        swagger_object['swagger'] = Swagger.get_swagger_version()
        swagger_object['info'] = Swagger.get_info_object(title=api.title, version=version.name)
        swagger_object['host'] = Swagger.get_host(environment)
        swagger_object['basePath'] = Swagger.get_basePath(version.name)
        swagger_object['schemes'] = Swagger.get_schemes()
        swagger_object['paths'] = Swagger.get_paths(resources, endpoints)
        swagger_object['definitions'] = Swagger.get_object_definitions(resources)
        swagger_object['securityDefinitions'] = Swagger.get_security_definitions()

        #swagger_object['consumes'] = None
        #swagger_object['produces'] = None

        return json.dumps(swagger_object)

    @staticmethod
    def get_swagger_version():
        return "2.0"

    @staticmethod
    def get_info_object(**kwargs):
        info = {}
        info['title'] = kwargs['title']
        info['version'] = kwargs['version']

        return info

    @staticmethod
    def get_host(environment):
        if environment.lower() == 'sandbox':
            return 'sandbox.magicstack.io'
        else:
            return 'api.magickstack.io'

    @staticmethod
    def get_basePath(version_name):
        return '/'+version_name

    @staticmethod
    def get_schemes():
        return 'http, https'

    @staticmethod
    def get_paths(resources, endpoints):
        paths = {}

        for endpoint in endpoints:
            for tmp in resources:
                if endpoint.resource_id == tmp.id:
                    resource = tmp

            print "getting path for: "+endpoint.method
            print endpoint

            status_code = "201" if endpoint.method == 'post' else '200'
            response_type = "array" if endpoint.collection == True else "object"

            if endpoint.relative_url not in paths:
                paths[endpoint.relative_url] = {}
                paths[endpoint.relative_url]['x-singular'] = resource.name

            paths[endpoint.relative_url][endpoint.method] = {}
            paths[endpoint.relative_url][endpoint.method]['description'] = endpoint.description
            paths[endpoint.relative_url][endpoint.method]['produces'] = endpoint.produces
            paths[endpoint.relative_url][endpoint.method]['consumes'] = endpoint.consumes
            paths[endpoint.relative_url][endpoint.method]['responses'] = {}
            paths[endpoint.relative_url][endpoint.method]['responses'][status_code] = {}
            paths[endpoint.relative_url][endpoint.method]['responses'][status_code]['description'] = endpoint.name
            paths[endpoint.relative_url][endpoint.method]['responses'][status_code]['schema'] = {}
            paths[endpoint.relative_url][endpoint.method]['responses'][status_code]['schema']['type'] = response_type
            paths[endpoint.relative_url][endpoint.method]['responses'][status_code]['schema']['items'] = {}
            paths[endpoint.relative_url][endpoint.method]['responses'][status_code]['schema']['items']['$ref'] = '#/definitions/'+resource.name
            paths[endpoint.relative_url][endpoint.method]['security'] = []

            if resource.template and resource.template.lower() == 'user':
                paths[endpoint.relative_url][endpoint.method]['security'].append({"api_key":[]})
            else:
                paths[endpoint.relative_url][endpoint.method]['security'].append({"oauth2":['*']})

        '''
        for resource in resources:
            paths[resource.plurality] = {}
            paths[resource.plurality]['x-singular'] = resource.name

            for endpoint in endpoints:
                if endpoint.resource_id == resource.id:
                    status_code = "201" if endpoint.method == 'post' else '200'
                    response_type = "array" if endpoint.collection == True else "object"

                    paths[resource.plurality][endpoint.method] = {}
                    paths[resource.plurality][endpoint.method]['description'] = endpoint.description
                    paths[resource.plurality][endpoint.method]['produces'] = endpoint.produces
                    paths[resource.plurality][endpoint.method]['consumes'] = endpoint.consumes
                    paths[resource.plurality][endpoint.method]['responses'] = {}
                    paths[resource.plurality][endpoint.method]['responses'][status_code] = {}
                    paths[resource.plurality][endpoint.method]['responses'][status_code]['description'] = endpoint.name
                    paths[resource.plurality][endpoint.method]['responses'][status_code]['schema'] = {}
                    paths[resource.plurality][endpoint.method]['responses'][status_code]['schema']['type'] = response_type
                    paths[resource.plurality][endpoint.method]['responses'][status_code]['schema']['items'] = {}
                    paths[resource.plurality][endpoint.method]['responses'][status_code]['schema']['items']['$ref'] = '#/definitions/'+resource.name
                    paths[resource.plurality][endpoint.method]['security'] = []

                    if resource.template.lower() == 'user':
                        paths[resource.plurality][endpoint.method]['security'].append({"api_key":[]})
                    else:
                        paths[resource.plurality][endpoint.method]['security'].append({"oauth2":['*']})


                    # this is where i'll handle error payloads
                    #paths[resource.plurality][endpoint.method]['responses']['default'] = {}
        '''

        return paths

    @staticmethod
    def get_object_definitions(resources):
        definitions = {}

        for resource in resources:
            required_parameters = []
            definitions[resource.name] = {}
            definitions[resource.name]['type'] = "object"
            definitions[resource.name]['properties'] = {}

            for parameter in resource.parameters:
                definitions[resource.name]['properties'][parameter['name']] = {}
                definitions[resource.name]['properties'][parameter['name']]["type"] = parameter['type']
                definitions[resource.name]['properties'][parameter['name']]["description"] = parameter['description']
                definitions[resource.name]['properties'][parameter['name']]["readOnly"] = parameter['read_only']

                if parameter['required']:
                    required_parameters.append(parameter['name'])

            if required_parameters:
                definitions[resource.name]['required'] = required_parameters

        return definitions

    @staticmethod
    def get_security_definitions():
        definitions = {}
        definitions['api_key'] = {}
        definitions['api_key']['type'] = 'apiKey'
        definitions['api_key']['name'] = 'x-magicstack-key'
        definitions['api_key']['in'] = 'header'

        definitions['oauth2'] = {}
        definitions['oauth2']['type'] = 'oauth2'
        definitions['oauth2']['flow'] = 'password'
        definitions['oauth2']['tokenUrl'] = 'http://sandbox.magicstack.io/oauth2/token'
        definitions['oauth2']['scopes'] = {"*":"all access"}

        return definitions

