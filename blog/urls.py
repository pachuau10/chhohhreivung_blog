from django.urls import path, include
from . import views
from .feeds import LatestArticlesFeed

urlpatterns = [
    path("", views.home, name="home"),
    path("news/<slug:slug>/", views.article_detail, name="article_detail"),
    path("category/<slug:slug>/", views.category_view, name="category"),
    path("search/", views.search_view, name="search"),
    path("search/suggest/", views.search_suggest, name="search_suggest"),
    path("rss/", LatestArticlesFeed(), name="rss_feed"),
    path("feed/", LatestArticlesFeed(), name="rss_feed_alt"),
    path("register/", views.register, name="register"),
    path("post/new/", views.post_writer, name="post_writer_new"),
    path("post/edit/<int:article_id>/", views.post_writer, name="post_writer_edit"),
]
