import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'dev-ypnvxc34.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'Coffee'


class AuthError(Exception):
    '''
    AuthError Exception
    A standardized way to communicate auth failure modes
    '''

    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header
def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()

    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token


'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''


def check_permissions(permission, payload):
    '''
    check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    (1) it raise an AuthError if permissions are not included in the payload,
    (2) it raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
    '''

    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions are not included in the JWT.'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 401)
    return True


def verify_decode_jwt(token):
    '''
    verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)
    Auth0 token with key id (kid)
    verify the token using Auth0 /.well-known/jwks.json
    should decode the payload from the token
    should validate the claims
    return the decoded payload
    '''

    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverifiedHeader = jwt.get_unverified_header(token)
    if 'kid' not in unverifiedHeader:
        raise AuthError({
            'code': 'Invalid Header',
            'description': 'Authorization malformed'
        }, 401)

    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == unverifiedHeader['kid']:
            rsa_key = {
                'alg': key['alg'],
                'kty': key['kty'],
                'use': key['use'],
                'kid': key['kid'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)
        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims check the audiance and issuer'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'Invalid header',
                'description': 'Unable to parse autherication token'
            }, 400)
    raise AuthError({
        'code': 'Invalid Header',
        'description': 'Unable to find the appropriate key'
    }, 401)


def requires_auth(permission=''):
    '''
    @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it use the get_token_auth_header method to get the token
    it use the verify_decode_jwt method to decode the jwt
    it use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
    '''
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator
