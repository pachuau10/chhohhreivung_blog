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


def get_nav_menu_items(current_path):
    return [{"label": "Home", "url": "/", "icon": "🏠", "active": current_path == "/"}]


def site_context(request):
    categories = Category.objects.filter(name__in=["AI", "Apple", "Cybersecurity", "Science", "Tutorial"])
    trending = Article.objects.defer("content", "meta_title", "meta_description", "meta_keywords").filter(status="published").order_by("-views")[:5]
    latest_sidebar = Article.objects.defer("content", "meta_title", "meta_description", "meta_keywords").filter(status="published").order_by("-published_at")[:5]

    return {
        "site_name": "Chhohreivung",
        "site_description": "Chhohreivung hi Mizoṭawnga Technology News chhiar theihna website a ni. Technology chanchinthar ber ber te rawn hria in rawn chhiar ve ta che.",
        "categories": categories,
        "nav_menu_items": get_nav_menu_items(request.path),
        "trending_articles": trending,
        "latest_sidebar": latest_sidebar,
        "search_form": SearchForm(),
        "current_path": request.path,
    }
