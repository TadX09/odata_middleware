import logging
import traceback
from typing import Union

from fastapi import Request
from sqlalchemy.exc import OperationalError

from app.xm_json_response import JsonOrXmlResponse

logging_level_selector = {
    'WARNING': logging.warning,
    'ERROR': logging.error,
    'INFO': logging.info,
    'CRITICAL': logging.critical,
    'FATAL': logging.fatal
}


class DoesNotExist(Exception):
    pass


def does_not_exist_handler(request: Request, exc: DoesNotExist):
    response = JsonOrXmlResponse(["obj not found"], request, status_code=404)
    _log_traceback(exc, request, response, 'WARNING')
    return response


def exception_handler(request: Request, exc: Union[Exception, OperationalError]):
    response = JsonOrXmlResponse("Unexpected exception", request, status_code=500)
    _log_traceback(exc, request, response, 'ERROR')
    return response


def _log_traceback(exc, request, response, severity):
    traceback_str = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    log_entry = {
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host,
        "traceback2": traceback_str,
        "response_id": response.response_id
    }
    logging_level_selector[severity](log_entry)

