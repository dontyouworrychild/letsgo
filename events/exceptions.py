from rest_framework.exceptions import APIException


class ApiException(APIException):
    status_code = 400
    default_detail = 'Bad request error'
    default_code = 'bad_request'
