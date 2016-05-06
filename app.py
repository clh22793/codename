from flask import Flask, json, request, make_response
import datetime, base64, logging

# internal imports
import customexception
from util import Util
from verifyrequest import VerifyRequest
from payload import UsersPayload
from payload import OauthPayload
from payload import ApiPayload
from models import model_user
from models import model_oauth
from models import model_api
from models import model_swagger

import requesthandlers

# APP BEGIN
app = Flask(__name__)

@app.errorhandler(Exception)
def unhandled_exception(exception):
    if exception.__class__.__name__ == "AuthException" or exception.__class__.__name__ == "HeaderException" or exception.__class__.__name__ == "ResourceException" or exception.__class__.__name__ == "PayloadException":
        error = {"error_code":exception.args[0], "error_message": customexception.error_codes_map[exception.args[0]]}
    else:
        logging.exception(exception)
        error = {"error_code":10010, "error_message": "internal api error"}

    response = make_response(json.dumps(error), 400)
    return response

@app.route('/')
def index():
    return 'In the beginning, there was a command line...'

@app.route('/clients', methods=['POST'])
def clients():
    clienthandler = requesthandlers.ClientHandler()
    return clienthandler.process(request=request)

@app.route('/users', methods=['POST'])
def users():
    userhandler = requesthandlers.UserHandler()
    return userhandler.process(request=request)

@app.route('/oauth2/token', methods=['POST'])
def token():
    oauthhandler = requesthandlers.OauthHandler()
    return oauthhandler.process(request=request)

@app.route('/apis', methods=['POST', 'GET'])
def apis():
    apihandler = requesthandlers.ApiHandler()
    return apihandler.process(request=request)

@app.route('/apis/<api_id>', methods=['GET'])
def apis_by_id(api_id):
    apihandler = requesthandlers.ApiHandler()
    return apihandler.process(request=request, api_id=api_id)

@app.route('/apis/<api_id>/versions', methods=['POST', 'GET'])
def versions(api_id):
    versionhandler = requesthandlers.VersionHandler()
    return versionhandler.process(request=request, api_id=api_id)

@app.route('/versions/<version_id>/resources', methods=['POST', 'GET'])
def resources(version_id):
    resourcehandler = requesthandlers.ResourceHandler()
    return resourcehandler.process(request=request, version_id=version_id)

@app.route('/resources/<resource_id>', methods=['GET'])
def resources_by_id(resource_id):
    resourcehandler = requesthandlers.ResourceHandler()
    return resourcehandler.process(request=request, resource_id=resource_id)

@app.route('/versions/<version_id>/swaggers', methods=['POST'])
def swaggers(version_id):
    swaggerhandler = requesthandlers.SwaggerHandler()
    return swaggerhandler.process(request=request, version_id=version_id)

@app.route('/data')
def names():
    data = {"names": ["Chris", "Hank", "Harry", "joe"]}
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
