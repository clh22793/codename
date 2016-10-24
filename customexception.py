# error codes
invalid_client = 100
invalid_token = 101
invalid_user_creds = 102
invalid_token_type = 103
invalid_content_type = 104

user_already_exists = 201
saasdoc_already_exists = 202
version_already_exists = 203
endpoint_already_exists = 204
section_already_exists = 205
resource_already_exists = 207
api_already_exists = 208
swagger_already_exists = 209

saasdoc_not_found = 301
version_not_found = 302
section_not_found = 303
resource_not_found = 304
parent_resource_not_found = 305

invalid_payload = 401
missing_required_parameters = 402

permission_denied = 501
method_not_allowed = 502
cannot_delete_resource = 503
resource_has_children = 504

# error code / message map
error_codes_map = {}
error_codes_map[invalid_client] = "invalid client"
error_codes_map[invalid_token] = "invalid token"
error_codes_map[invalid_token_type] = "invalid token type"
error_codes_map[invalid_content_type] = "invalid content type"
error_codes_map[user_already_exists] = "user already exists"
error_codes_map[saasdoc_already_exists] = "saasdoc name already taken"
error_codes_map[invalid_user_creds] = "invalid user creds"
error_codes_map[saasdoc_not_found] = "could not find saasdoc"
error_codes_map[version_already_exists] = "version already exists"
error_codes_map[version_not_found] = "could not found version"
error_codes_map[section_not_found] = "could not found section"
error_codes_map[endpoint_already_exists] = "endpoint already exists"
error_codes_map[section_already_exists] = "Section already exists"
error_codes_map[invalid_payload] = "Invalid payload"
error_codes_map[permission_denied] = "Permission denied"
error_codes_map[resource_already_exists] = "Resource already exists"
error_codes_map[resource_not_found] = "Resource not found"
error_codes_map[method_not_allowed] = "Method not allowed"
error_codes_map[missing_required_parameters] = "Missing required parameters."
error_codes_map[parent_resource_not_found] = "Parent resource not found."
error_codes_map[cannot_delete_resource] = "Cannot delete resource."
error_codes_map[api_already_exists] = "API already exists."
error_codes_map[swagger_already_exists] = "Swagger already exists."
error_codes_map[resource_has_children] = "Cannot delete. This resource has at least one child resource."

class AuthException(Exception):
    pass

class HeaderException(Exception):
    pass

class ResourceException(Exception):
    pass

class PayloadException(Exception):
    pass