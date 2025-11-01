from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser
import logging

logger = logging.getLogger(__name__)

class JWTAuthenticationFromCookie:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get access token from cookie
        access_token = request.COOKIES.get('access_token')
        
        logger.info(f"=== JWT Middleware Debug ===")
        logger.info(f"Path: {request.path}")
        logger.info(f"Cookies: {list(request.COOKIES.keys())}")
        logger.info(f"Access Token Found: {bool(access_token)}")
        
        if access_token:
            # Set it in the Authorization header so DRF can use it
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            
            # Try to authenticate the user
            try:
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(access_token)
                user = jwt_auth.get_user(validated_token)
                request.user = user
                # Fixed: Use str(user) or user.email instead of user.username
                logger.info(f"User authenticated: {user.email if hasattr(user, 'email') else str(user)}")
            except (InvalidToken, TokenError) as e:
                logger.error(f"Token validation failed: {str(e)}")
                request.user = AnonymousUser()
        else:
            logger.info("No access token in cookies")
        
        response = self.get_response(request)
        return response