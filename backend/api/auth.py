from functools import wraps
from rest_framework.exceptions import AuthenticationFailed
import jwt
import requests
from django.conf import settings

def get_token_auth_header(request):
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    if auth is None:
        raise AuthenticationFailed('Authorization header is missing')
    parts = auth.split()
    if parts[0].lower() != "bearer":
        raise AuthenticationFailed('Authorization header must start with Bearer')
    return parts[1]

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        request = args[0]
        token = get_token_auth_header(request)
        jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
        jwks = requests.get(jwks_url).json()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=["RS256"],
                    audience=settings.AUTH0_AUDIENCE,
                    issuer=f"https://{settings.AUTH0_DOMAIN}/"
                )
                request.auth_payload = payload
            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed('Token is expired')
            except jwt.JWTClaimsError:
                raise AuthenticationFailed('Invalid claims')
            except Exception:
                raise AuthenticationFailed('Invalid token')
        else:
            raise AuthenticationFailed('No matching key found')
        return f(*args, **kwargs)
    return decorated