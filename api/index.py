import os
import sys
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chhohreivung.settings")

app = get_wsgi_application()

def handler(event, context):
    from urllib.parse import urlparse, unquote
    from io import BytesIO
    from django.http import HttpRequest, HttpResponse
    from django.core.handlers.wsgi import WSGIHandler
    from django.conf import settings

    method = event.get("httpMethod", "GET")
    path = event.get("path", "/")
    query = event.get("queryStringParameters") or {}
    headers = event.get("headers") or {}
    body = event.get("body") or ""
    is_base64 = event.get("isBase64Encoded", False)

    if is_base64:
        import base64
        body = base64.b64decode(body)
    else:
        body = body.encode("utf-8") if isinstance(body, str) else body

    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": unquote(path),
        "QUERY_STRING": "&".join(f"{k}={v}" for k, v in query.items()) if query else "",
        "SERVER_NAME": headers.get("host", "localhost"),
        "SERVER_PORT": "443",
        "SERVER_PROTOCOL": "HTTP/1.1",
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "https",
        "wsgi.input": BytesIO(body),
        "wsgi.errors": sys.stderr,
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
        "HTTP_HOST": headers.get("host", ""),
        "HTTP_X_FORWARDED_FOR": headers.get("x-forwarded-for", ""),
        "HTTP_X_FORWARDED_PROTO": "https",
        "HTTP_USER_AGENT": headers.get("user-agent", ""),
        "HTTP_ACCEPT": headers.get("accept", "*/*"),
        "CONTENT_TYPE": headers.get("content-type", ""),
        "CONTENT_LENGTH": str(len(body)),
    }

    for key, value in headers.items():
        wsgi_key = "HTTP_" + key.upper().replace("-", "_")
        environ[wsgi_key] = value

    response = HttpResponse()

    def start_response(status, response_headers):
        status_code = int(status.split(" ")[0])
        response.status_code = status_code
        for header, value in response_headers:
            response[header] = value

    result = app(environ, start_response)
    response.content = b"".join(result)

    return {
        "statusCode": response.status_code,
        "headers": dict(response.items()),
        "body": response.content.decode("utf-8", errors="replace"),
        "isBase64Encoded": False,
    }
