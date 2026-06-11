from .models import Category, Article
from .forms import SearchForm


NAV_MENU_ICONS = {
    "ai": "🤖",
    "apps": "📱",
    "cybersecurity": "🔒",
    "how-to": "📚",
    "internet": "🌐",
    "reviews": "⭐",
    "gaming": "🎮",
    "science": "🔬",
    "startups": "🚀",
}


def get_nav_menu_items(categories, current_path):
    items = [{"label": "Home", "url": "/", "icon": "🏠", "active": current_path == "/"}]
    for cat in categories:
        slug = cat.slug.lower()
        icon = NAV_MENU_ICONS.get(slug, "📄")
        active = slug in current_path and current_path != "/"
        items.append({"label": cat.name, "url": f"/category/{cat.slug}/", "icon": icon, "active": active})
    return items


def site_context(request):
    categories = Category.objects.all()
    trending = Article.objects.defer("content", "meta_title", "meta_description", "meta_keywords").filter(status="published").order_by("-views")[:5]
    latest_sidebar = Article.objects.defer("content", "meta_title", "meta_description", "meta_keywords").filter(status="published").order_by("-published_at")[:5]

    return {
        "site_name": "Chhohreivung",
        "site_description": "Mizo Tech News - Technology news in Mizo language",
        "categories": categories,
        "nav_menu_items": get_nav_menu_items(categories, request.path),
        "trending_articles": trending,
        "latest_sidebar": latest_sidebar,
        "search_form": SearchForm(),
        "current_path": request.path,
    }
