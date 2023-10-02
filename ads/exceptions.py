import logging

from rest_framework import exceptions
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework.views import set_rollback, status

logger = logging.getLogger(__name__)


def ads_api_exception_handler(exc, context):

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        if isinstance(exc, exceptions.ValidationError):
            data = {
                "code": 101,
                "msg": "Invalid Request",
                "detail": exc.get_full_details()
            }

        elif isinstance(exc, exceptions.ParseError):
            data = {
                "code": 102,
                "msg": "Malformed Request",
            }

        elif isinstance(exc, exceptions.MethodNotAllowed):
            data = {
                "code": 103,
                "msg": "This HTTP method not allowed on this endpoint",
            }

        elif isinstance(exc, exceptions.Throttled):
            data = {
                "code": 104,
                "msg": "Too many requests",
            }

        elif isinstance(exc, exceptions.NotAuthenticated):
            data = {
                "code": 105,
                "msg": "Not authenticated",
            }

        elif isinstance(exc, exceptions.AuthenticationFailed):
            data = {
                "code": 106,
                "msg": "Invalid token",
            }

        elif isinstance(exc, exceptions.NotFound):
            data = {
                "code": 107,
                "msg": "Requested resource not found",
            }

        elif isinstance(exc, exceptions.PermissionDenied):
            data = {
                "code": 108,
                "msg": "You dont have permission",
            }

        else:
            logger.exception(exc)
            data = {
                "code": 100,
                "msg": "Unhandled Exception",
            }

        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)

    elif isinstance(exc, Http404):
        data = {
            "code": 107,
            "msg": "Requested resource not found",
        }
        return Response(data, status=status.HTTP_404_NOT_FOUND)

    else:
        logger.exception(str(exc))
        return Response(
            {
                "code": 1000,
                "msg": "Server Error"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
