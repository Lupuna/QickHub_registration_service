from rest_framework import status
from rest_framework.exceptions import APIException


class TwoCommitsError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'problem with two commits'
    default_code = 'error'