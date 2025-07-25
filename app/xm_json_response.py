import datetime
import logging
import uuid
from typing import Any

from dicttoxml import dicttoxml
from fastapi import Request
from fastapi.responses import JSONResponse, Response


class JsonOrXmlResponse(Response):

    def __init__(self, content: Any, request: Request, **kwargs):
        self.response_id = str(uuid.uuid4())
        self.content = {
            "data": content,
            "metadata": {
                "timestamp": datetime.datetime.utcnow().isoformat() + 'Z',
                "responseId": self.response_id
            }
        }
        self.request = request
        super().__init__(**kwargs)
        log_entry = {
            "method": request.method,
            "url": str(request.url),
            "status_code": self.status_code,
            "client_ip": request.client.host,
            "responseId": self.response_id
        }
        logging.info(log_entry)

    def render(self, content: Any) -> bytes:
        accept_header = self.request.headers.get("accept")
        response_data = content or self.content

        if "application/xml" in accept_header:
            return self.to_xml(response_data)
        else:
            return self.to_json(response_data)

    def to_json(self, content: Any) -> bytes:
        self.media_type = "application/json"
        return JSONResponse(content=content).body

    def to_xml(self, content: Any) -> bytes:
        self.media_type = "application/xml"
        return dicttoxml(content)
