from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from .sitemaps import sitemap_view
from .robots import robots_view
from blog import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("blog.urls")),
    path("sitemap.xml", sitemap_view, name="sitemap"),
    path("robots.txt", robots_view, name="robots"),
    path("about/", TemplateView.as_view(template_name="about.html"), name="about"),
    path("contact/", views.contact_view, name="contact"),
    path("privacy-policy/", TemplateView.as_view(template_name="privacy.html"), name="privacy"),
    path("terms/", TemplateView.as_view(template_name="terms.html"), name="terms"),
]

if settings.DEBUG:
    if not settings.USE_CLOUDINARY:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "blog.views.page_not_found"
handler500 = "blog.views.server_error"