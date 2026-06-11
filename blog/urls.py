from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("news/<slug:slug>/", views.article_detail, name="article_detail"),
    path("category/<slug:slug>/", views.category_view, name="category"),
    path("search/", views.search_view, name="search"),
    path("search/suggest/", views.search_suggest, name="search_suggest"),
    path("register/", views.register, name="register"),
    path("post/new/", views.post_writer, name="post_writer_new"),
    path("post/edit/<int:article_id>/", views.post_writer, name="post_writer_edit"),
]
