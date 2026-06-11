from django.contrib.syndication.views import Feed
from django.urls import reverse
from .models import Article


class LatestArticlesFeed(Feed):
    title = "Chhohreivung - Mizo Tech News"
    link = "/"
    description = "Latest technology news in Mizo language"

    def items(self):
        return Article.objects.filter(status="published").order_by("-published_at")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt

    def item_link(self, item):
        return item.get_absolute_url()

    def item_pubdate(self, item):
        return item.published_at

    def item_author_name(self, item):
        if item.author:
            return item.author.get_full_name() or item.author.username
        return "Chhohreivung"
