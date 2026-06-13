from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from .models import Article, Category, Tag, PageView
from .forms import SearchForm, ContactForm, PostForm


def home(request):
    base_qs = Article.objects.select_related("category").defer(
        "content", "meta_title", "meta_description", "meta_keywords"
    ).filter(status="published")
    featured = base_qs.filter(featured=True).first()
    latest = base_qs.order_by("-published_at")[:12]
    popular = base_qs.order_by("-views")[:6]
    categories = Category.objects.filter(name__in=["AI", "Apple", "Cybersecurity", "Science", "Tutorial"])

    category_articles = {}
    for cat in categories:
        articles = base_qs.filter(category=cat).order_by("-published_at")[:4]
        if articles:
            category_articles[cat] = articles

    hero_articles = list(base_qs.order_by("-published_at")[:5])

    context = {
        "featured_article": featured,
        "latest_articles": latest,
        "latest_news": latest,
        "popular_articles": popular,
        "category_articles": category_articles,
        "hero_articles": hero_articles,
        "show_hero": True,
    }
    return render(request, "home.html", context)


def article_detail(request, slug):
    article = get_object_or_404(
        Article.objects.select_related("category", "author"),
        slug=slug, status="published"
    )
    article.increment_views()

    ip = request.META.get("REMOTE_ADDR", "0.0.0.0")
    if ip != "0.0.0.0":
        PageView.objects.create(
            article=article,
            path=request.path,
            ip_address=ip,
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            session_key=request.session.session_key or "",
        )

    list_qs = Article.objects.defer("content", "meta_title", "meta_description", "meta_keywords").filter(status="published")
    related = list_qs.filter(
        category=article.category
    ).exclude(id=article.id)[:4]

    popular = list_qs.order_by("-views")[:5]

    prev_article = list_qs.filter(
        published_at__lt=article.published_at
    ).order_by("-published_at").first()

    next_article = list_qs.filter(
        published_at__gt=article.published_at
    ).order_by("published_at").first()

    context = {
        "article": article,
        "related_articles": related,
        "popular_articles": popular,
        "prev_article": prev_article,
        "next_article": next_article,
        "meta_title": article.meta_title,
        "meta_description": article.meta_description,
        "meta_keywords": article.meta_keywords,
        "canonical_url": article.get_absolute_url(),
    }
    return render(request, "article_detail.html", context)


def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles_list = Article.objects.defer(
        "content", "meta_title", "meta_description", "meta_keywords"
    ).filter(status="published", category=category).order_by("-published_at")

    paginator = Paginator(articles_list, 10)
    page = request.GET.get("page", 1)
    articles = paginator.get_page(page)

    context = {
        "category": category,
        "articles": articles,
        "meta_title": f"{category.name} - Chhohreivung",
        "meta_description": category.description or f"Latest {category.name} news in Mizo",
    }
    return render(request, "category.html", context)


def search_suggest(request):
    query = request.GET.get("q", "").strip()
    results = []
    if len(query) >= 2:
        results = Article.objects.select_related("category").defer(
            "content", "meta_title", "meta_description", "meta_keywords"
        ).filter(
            Q(status="published"),
            Q(title__icontains=query)
            | Q(excerpt__icontains=query)
            | Q(category__name__icontains=query)
            | Q(tags__name__icontains=query),
        ).distinct().order_by("-published_at")[:6]

    html = render_to_string("includes/search_suggestions.html", {
        "results": results,
        "query": query,
    })
    return JsonResponse({"html": html, "count": len(results)})


def contact_view(request):
    form = ContactForm()
    success = False
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            from .models import ContactMessage
            ContactMessage.objects.create(
                name=form.cleaned_data["name"],
                email=form.cleaned_data["email"],
                subject=form.cleaned_data["subject"],
                message=form.cleaned_data["message"],
            )
            try:
                form.send_email()
                messages.success(request, "Thank you! Your message has been sent.")
                success = True
                form = ContactForm()
            except Exception:
                messages.success(request, "Thank you! Your message has been received.")
                success = True
                form = ContactForm()
        else:
            messages.error(request, "Please correct the errors below.")
    context = {
        "form": form,
        "success": success,
        "meta_title": "Contact Us - Chhohreivung",
        "meta_description": "Get in touch with Chhohreivung team.",
    }
    return render(request, "contact.html", context)


@staff_member_required
def post_writer(request, article_id=None):
    from django.utils.text import slugify
    instance = None
    if article_id:
        instance = get_object_or_404(Article, id=article_id)

    form = PostForm(instance=instance)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            article = form.save(commit=False)
            if not article.author_id:
                article.author = request.user
            if article.status == "published" and not article.published_at:
                article.published_at = timezone.now()
            if not article.slug:
                article.slug = slugify(article.title)
            article.save()
            form.save_m2m()
            if 'preview' in request.POST:
                return redirect(article.get_absolute_url())
            msg = "Article published!" if article.status == "published" else "Draft saved!"
            messages.success(request, msg)
            return redirect("post_writer_edit", article_id=article.id)

    categories = Category.objects.all()
    tags = Tag.objects.all()
    return render(request, "post_writer.html", {
        "form": form,
        "article": instance,
        "categories": categories,
        "tags": tags,
        "title": "Edit Article" if instance else "New Article",
    })


def register(request):
    from django.contrib.auth.models import User
    if User.objects.filter(is_superuser=True).exists():
        return redirect("home")
    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm", "")
        if not username or not email or not password:
            error = "All fields are required."
        elif password != confirm:
            error = "Passwords do not match."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif User.objects.filter(username=username).exists():
            error = "Username already taken."
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            return redirect("admin:index")
    return render(request, "register.html", {"error": error})


def page_not_found(request, exception):
    return render(request, "404.html", status=404)


def server_error(request):
    return render(request, "500.html", status=500)


def search_view(request):
    query = request.GET.get("q", "").strip()
    results = []
    list_qs = Article.objects.defer("content", "meta_title", "meta_description", "meta_keywords")
    popular = list_qs.filter(status="published").order_by("-views")[:5]

    if query:
        results = list_qs.filter(
            Q(status="published"),
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(excerpt__icontains=query)
            | Q(category__name__icontains=query)
            | Q(tags__name__icontains=query),
        ).distinct().order_by("-published_at")

    context = {
        "query": query,
        "results": results,
        "popular_articles": popular,
        "meta_title": f"Search: {query}" if query else "Search - Chhohreivung",
        "meta_description": "Search technology news articles in Mizo language",
    }
    return render(request, "search.html", context)

