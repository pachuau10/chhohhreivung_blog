from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
from .models import Article, PageView, Income, Category, ContactMessage


@staff_member_required
def admin_dashboard(request):
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    twelve_months_ago = now - timedelta(days=365)

    total_articles = Article.objects.filter(status="published").count()
    total_drafts = Article.objects.filter(status="draft").count()
    total_categories = Category.objects.count()
    total_views = Article.objects.aggregate(total=Sum("views"))["total"] or 0

    unique_visitors = (
        PageView.objects.values("ip_address")
        .distinct()
        .count()
    )

    views_30d = (
        PageView.objects.filter(viewed_at__gte=thirty_days_ago)
        .count()
    )

    unique_30d = (
        PageView.objects.filter(viewed_at__gte=thirty_days_ago)
        .values("ip_address")
        .distinct()
        .count()
    )

    popular_articles = (
        Article.objects.filter(status="published")
        .annotate(
            unique_views=Count("page_views", distinct=True),
            recent_views=Count(
                "page_views",
                filter=Q(page_views__viewed_at__gte=thirty_days_ago),
                distinct=True,
            ),
        )
        .order_by("-views")[:10]
    )

    daily_views = (
        PageView.objects.filter(viewed_at__gte=thirty_days_ago)
        .annotate(date=TruncDate("viewed_at"))
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )

    daily_labels = [d["date"].strftime("%b %d") for d in daily_views]
    daily_data = [d["count"] for d in daily_views]

    monthly_views = (
        PageView.objects.filter(viewed_at__gte=twelve_months_ago)
        .annotate(month=TruncMonth("viewed_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )

    monthly_labels = [m["month"].strftime("%b %Y") for m in monthly_views]
    monthly_data = [m["count"] for m in monthly_views]

    total_income = Income.objects.aggregate(total=Sum("amount"))["total"] or 0

    income_12m = (
        Income.objects.filter(date__gte=twelve_months_ago.date())
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    income_labels = [i["month"].strftime("%b %Y") for i in income_12m]
    income_data = [float(i["total"]) for i in income_12m]

    income_by_source = (
        Income.objects.values("source")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    recent_income = Income.objects.order_by("-date")[:10]

    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    recent_messages = ContactMessage.objects.order_by("-created_at")[:10]

    context = {
        "total_articles": total_articles,
        "total_drafts": total_drafts,
        "total_categories": total_categories,
        "total_views": total_views,
        "unique_visitors": unique_visitors,
        "views_30d": views_30d,
        "unique_30d": unique_30d,
        "popular_articles": popular_articles,
        "daily_labels": daily_labels,
        "daily_data": daily_data,
        "monthly_labels": monthly_labels,
        "monthly_data": monthly_data,
        "total_income": total_income,
        "income_labels": income_labels,
        "income_data": income_data,
        "income_by_source": income_by_source,
        "recent_income": recent_income,
        "unread_messages": unread_messages,
        "recent_messages": recent_messages,
        "title": "Dashboard",
    }
    return render(request, "admin/dashboard.html", context)
