from django.http import HttpResponse
from django.conf import settings


def robots_view(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /private/",
        "",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
        "",
        "User-agent: GPTBot",
        "Disallow: /",
        "",
        "User-agent: ChatGPT-User",
        "Disallow: /",
        "",
        "User-agent: CCBot",
        "Disallow: /",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
