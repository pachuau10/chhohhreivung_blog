from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.utils import timezone
from .models import Category, Tag, Article, PageView, Income, ContactMessage
from .dashboard import admin_dashboard


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name", "slug", "article_count"]
    search_fields = ["name"]

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = "Articles"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ["name", "slug"]
    search_fields = ["name"]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    change_form_template = "admin/blog/article/change_form.html"
    prepopulated_fields = {"slug": ("title",)}
    list_display = [
        "title", "category", "status", "featured", "views",
        "published_at", "reading_time_display"
    ]
    list_filter = ["status", "featured", "category", "tags"]
    search_fields = ["title", "excerpt", "content"]
    date_hierarchy = "published_at"
    filter_horizontal = ["tags"]
    actions = ["make_published", "make_draft", "toggle_featured"]

    fieldsets = [
        ("Content", {
            "fields": ["title", "slug", "excerpt", "content", "featured_image"]
        }),
        ("Metadata", {
            "fields": ["category", "tags", "author"],
            "classes": ["collapse"]
        }),
        ("SEO", {
            "fields": ["meta_title", "meta_description", "meta_keywords"],
            "classes": ["collapse"]
        }),
        ("Publishing", {
            "fields": ["status", "featured", "published_at"]
        }),
    ]

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        if obj.status == "published" and not obj.published_at:
            from django.utils import timezone
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)

    def reading_time_display(self, obj):
        return f"{obj.reading_time()} min"
    reading_time_display.short_description = "Reading Time"

    def make_published(self, request, queryset):
        from django.utils import timezone
        queryset.update(status="published", published_at=timezone.now())
    make_published.short_description = "Mark selected as published"

    def make_draft(self, request, queryset):
        queryset.update(status="draft")
    make_draft.short_description = "Mark selected as draft"

    def toggle_featured(self, request, queryset):
        for article in queryset:
            article.featured = not article.featured
            article.save()
    toggle_featured.short_description = "Toggle featured status"


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ["path", "ip_address", "viewed_at"]
    list_filter = ["viewed_at"]
    date_hierarchy = "viewed_at"
    search_fields = ["path", "ip_address"]
    readonly_fields = ["article", "path", "ip_address", "user_agent", "session_key", "viewed_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ["date", "source", "amount", "description"]
    list_filter = ["source", "date"]
    search_fields = ["description", "notes"]
    date_hierarchy = "date"
    list_select_related = False

    fieldsets = [
        (None, {
            "fields": ["amount", "source", "date"]
        }),
        ("Details", {
            "fields": ["description", "notes"]
        }),
    ]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "subject", "created_at", "is_read"]
    list_filter = ["is_read", "created_at"]
    search_fields = ["name", "email", "subject", "message"]
    date_hierarchy = "created_at"
    readonly_fields = ["name", "email", "subject", "message", "created_at"]
    actions = ["mark_as_read"]

    def has_add_permission(self, request):
        return False

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected as read"


# Add dashboard URL to admin
original_get_urls = admin.site.get_urls

def patched_get_urls():
    urls = original_get_urls()
    urls.insert(0, path("dashboard/", admin.site.admin_view(admin_dashboard), name="admin_dashboard"))
    return urls

admin.site.get_urls = patched_get_urls
