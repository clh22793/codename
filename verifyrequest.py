import re
# internal imports
import customexception
from models import model_client
from models import model_oauth

# AUTHORIZATION ==========
class VerifyRequest:
    _content_type_formencoded = 'application/x-www-form-urlencoded'
    _content_type_json = 'application/json'

    @staticmethod
    def authorization(type, request):
        clients = model_client()
        oauths = model_oauth()

        auth_header = request.headers['Authorization'].split()

        if type.lower() == 'basic':
            # basic authorization
            client = clients.get(token=auth_header[1], active=True)
            #print client

            if not client._id:
                raise customexception.AuthException(customexception.invalid_client)
            else:
                return client
        elif type.lower() == 'bearer':
            # bearer authorization
            #print "TOKEN:"
            #print auth_header[1]

            oauth = oauths.get(access_token=auth_header[1], active=True)

            if not oauth:
                raise customexception.AuthException(customexception.invalid_token)
            else:
                return oauth
        else:
            raise customexception.AuthException(customexception.invalid_token_type)


    # DEPRECATED
    @staticmethod
    def verifyContentType(type, request):
        match = re.match(type, request.headers['Content-Type'])
        if not match:
            raise customexception.HeaderException(customexception.invalid_content_type)
