from flask import Flask, json, request, make_response
import datetime, base64, logging, requests

# internal imports
import customexception
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
    return 'In the Beginning... Was the Command Line'

'''
@app.route('/admin')
def admin():
    adminhandler = requesthandlers.AdminHandler()
    return adminhandler.get()
'''

@app.route('/invite_beta_users')
def beta():
    betas = requesthandlers.BetaHandler()
    return betas.invite()

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

@app.route('/resources/<resource_id>', methods=['PUT', 'GET', 'DELETE'])
def resources_by_id(resource_id):
    resourcehandler = requesthandlers.ResourceHandler()
    return resourcehandler.process(request=request, resource_id=resource_id)

@app.route('/resources/<resource_id>/endpoints', methods=['POST', 'GET'])
def endpoints(resource_id):
    endpointhandler = requesthandlers.EndpointHandler()
    return endpointhandler.process(request=request, resource_id=resource_id)

@app.route('/versions/<version_id>/deployments', methods=['POST', 'GET'])
def deployments(version_id):
    deploymenthandler = requesthandlers.DeploymentHandler()
    return deploymenthandler.process(request=request, version_id=version_id)

@app.route('/batch', methods=['POST'])
def batch():
    datas = json.loads(request.get_data())
    batch_responses = []

    print "datas:"
    print datas
    for data in datas:
        method = data['method']
        relative_url = data['relative_url']
        body = data['body']
        print "data:"
        print data
        r = requests.post('http://localhost:5000/'+relative_url, data = body, headers=request.headers)

        print "response:"
        print r.json()
        batch_responses.append(r.json())

    print "batch_responses:"
    print batch_responses

    response = make_response(json.dumps(batch_responses), 200)
    return response

    #endpointhandler = requesthandlers.EndpointHandler()
    #return endpointhandler.process(request=request, resource_id=resource_id)

@app.route('/versions/<version_id>/swaggers', methods=['POST'])
def swaggers(version_id):
    swaggerhandler = requesthandlers.SwaggerHandler()
    return swaggerhandler.process(request=request, version_id=version_id)

@app.route('/apis/<api_id>/keys', methods=['GET'])
def api_keys(api_id):
    apikeyshandler = requesthandlers.ApiKeysHandler()
    return apikeyshandler.process(request=request, api_id=api_id)

@app.route('/resources/<resource_id>/data', methods=['GET'])
def resources_data(resource_id):
    datahandler = requesthandlers.DataHandler()
    return datahandler.process(request=request, resource_id=resource_id)

# DEPRECATED; ONLY AN EXAMPLE!!
@app.route('/data')
def names():
    data = {"names": ["Chris", "Hank", "Harry", "joe"]}
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
