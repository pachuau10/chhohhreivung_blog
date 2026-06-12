from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.contrib.sitemaps import Sitemap
from blog.models import Article, Category, Tag


class ArticleSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Article.objects.filter(status="published")

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Category.objects.all()

    def lastmod(self, obj):
        return None


class TagSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Tag.objects.all()

    def lastmod(self, obj):
        return None


class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.3

    def items(self):
        return ["about", "contact", "privacy", "terms"]

    def location(self, item):
        return f"/{item}/"


def sitemap_view(request):
    urls = []

    articles = Article.objects.filter(status="published")
    for article in articles:
        urls.append({
            "location": f"/news/{article.slug}/",
            "lastmod": article.updated_at.strftime("%Y-%m-%d"),
            "changefreq": "daily",
            "priority": "0.9",
        })

    categories = Category.objects.all()
    for cat in categories:
        urls.append({
            "location": f"/category/{cat.slug}/",
            "lastmod": None,
            "changefreq": "weekly",
            "priority": "0.7",
        })

    static_pages = [
        {"location": "/", "priority": "1.0", "changefreq": "daily"},
        {"location": "/about/", "priority": "0.3", "changefreq": "monthly"},
        {"location": "/contact/", "priority": "0.3", "changefreq": "monthly"},
        {"location": "/privacy-policy/", "priority": "0.2", "changefreq": "monthly"},
        {"location": "/terms/", "priority": "0.2", "changefreq": "monthly"},
    ]
    urls = static_pages + urls

    template = loader.get_template("sitemap.xml")
    xml = template.render({"urls": urls, "site_url": settings.SITE_URL}, request)
    return HttpResponse(xml, content_type="application/xml")
