import os
import sys
from http.server import BaseHTTPRequestHandler

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chhohreivung.settings")

import django
django.setup()

from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse
from io import BytesIO

wsgi_app = get_wsgi_application()


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def do_PUT(self):
        self._handle_request()

    def do_PATCH(self):
        self._handle_request()

    def do_DELETE(self):
        self._handle_request()

    def do_HEAD(self):
        self._handle_request()

    def _handle_request(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        path_parts = self.path.split("?", 1)
        path_info = path_parts[0]
        query_string = path_parts[1] if len(path_parts) > 1 else ""

        environ = {
            "REQUEST_METHOD": self.command,
            "PATH_INFO": path_info,
            "QUERY_STRING": query_string,
            "SERVER_NAME": self.headers.get("Host", "localhost"),
            "SERVER_PORT": "443",
            "SERVER_PROTOCOL": "HTTP/1.1",
            "wsgi.version": (1, 0),
            "wsgi.url_scheme": "https",
            "wsgi.input": BytesIO(body),
            "wsgi.errors": sys.stderr,
            "wsgi.multithread": False,
            "wsgi.multiprocess": False,
            "wsgi.run_once": False,
            "HTTP_HOST": self.headers.get("Host", ""),
        }

        for key, value in self.headers.items():
            wsgi_key = "HTTP_" + key.upper().replace("-", "_")
            environ[wsgi_key] = value

        response = {}

        def start_response(status, response_headers):
            status_code = int(status.split(" ")[0])
            response["status"] = status_code
            response["headers"] = {}
            for header, value in response_headers:
                response["headers"][header] = value

        result = wsgi_app(environ, start_response)
        response["body"] = b"".join(result)

        self.send_response(response.get("status", 200))
        for header, value in response.get("headers", {}).items():
            self.send_header(header, value)
        self.end_headers()
        self.wfile.write(response.get("body", b""))
