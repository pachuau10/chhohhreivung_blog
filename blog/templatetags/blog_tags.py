from django import template
from django.utils.html import format_html, mark_safe
import re

register = template.Library()


@register.filter
def reading_time(content):
    word_count = len(re.findall(r"\w+", content))
    minutes = max(1, round(word_count / 200))
    return f"{minutes} min read"


@register.filter
def truncate_words(value, arg):
    try:
        limit = int(arg)
    except ValueError:
        return value
    words = value.split()
    if len(words) > limit:
        return " ".join(words[:limit]) + "..."
    return value


@register.filter
def date_format(value):
    from django.utils import timezone
    now = timezone.now()
    diff = now - value

    if diff.days == 0:
        if diff.seconds < 3600:
            minutes = diff.seconds // 60
            return f"{minutes} min ago" if minutes > 0 else "Just now"
        hours = diff.seconds // 3600
        return f"{hours} hour ago" if hours == 1 else f"{hours} hours ago"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return f"{diff.days} days ago"
    else:
        return value.strftime("%b %d, %Y")


@register.simple_tag(takes_context=True)
def og_tags(context, article=None):
    request = context.get("request")
    if not request:
        return ""

    static_url = context.get("STATIC_URL", "/static/")
    default_image = request.build_absolute_uri(static_url + "og_image.png")

    if article:
        title = (article.meta_title or article.title).strip()
        description = (article.meta_description or article.excerpt or article.title).strip()
        url = request.build_absolute_uri(article.get_absolute_url())
        image_url = default_image
        if article.featured_image:
            raw = article.featured_image.url
            if raw.startswith("http"):
                image_url = raw
                if "cloudinary" in raw:
                    if "." not in raw.rsplit("/", 1)[-1]:
                        image_url = raw + ".jpg"
                    image_url = image_url.replace("/upload/", "/upload/f_jpg,q_auto,w_1200/")
            else:
                image_url = request.build_absolute_uri(raw)
    else:
        title = (context.get("meta_title") or "Chhohreivung - Mizo Tech News").strip()
        description = (context.get("meta_description") or "Latest technology news in Mizo language").strip()
        url = request.build_absolute_uri(request.path)
        image_url = default_image

    from django.utils.html import escape
    e_title = escape(title)
    e_desc = escape(description)
    e_url = escape(url)
    e_image = escape(image_url) if image_url else ""
    og_type = "article" if article else "website"

    tags = (
        f'<meta property="og:title" content="{e_title}" />\n'
        f'<meta property="og:description" content="{e_desc}" />\n'
        f'<meta property="og:url" content="{e_url}" />\n'
        f'<meta property="og:type" content="{og_type}" />\n'
        f'<meta property="og:site_name" content="Chhohreivung" />\n'
        f'<meta property="og:locale" content="en_US" />\n'
    )
    if image_url:
        tags += (
            f'<meta property="og:image" content="{e_image}" />\n'
            f'<meta property="og:image:alt" content="{e_title}" />\n'
        )

    tags += (
        f'<meta name="twitter:card" content="summary_large_image" />\n'
        f'<meta name="twitter:title" content="{e_title}" />\n'
        f'<meta name="twitter:description" content="{e_desc}" />\n'
    )
    if image_url:
        tags += f'<meta name="twitter:image" content="{e_image}" />\n'

    return mark_safe(tags)


@register.simple_tag(takes_context=True)
def article_schema(context, article):
    request = context.get("request")
    if not request:
        return ""

    import json

    url = request.build_absolute_uri(article.get_absolute_url())
    image_url = ""
    if article.featured_image:
        image_url = request.build_absolute_uri(article.featured_image.url)

    schema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": article.title,
        "description": article.excerpt or article.title,
        "image": image_url,
        "datePublished": article.published_at.isoformat() if article.published_at else "",
        "dateModified": article.updated_at.isoformat(),
        "author": {
            "@type": "Person",
            "name": article.author.get_full_name() or article.author.username if article.author else "Chhohreivung"
        },
        "publisher": {
            "@type": "Organization",
            "name": "Chhohreivung",
            "logo": {
                "@type": "ImageObject",
                "url": request.build_absolute_uri("/static/images/logo.png")
            }
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": url
        }
    }
    return mark_safe(
        '<script type="application/ld+json">' +
        json.dumps(schema, ensure_ascii=False, indent=2) +
        "</script>"
    )


@register.simple_tag(takes_context=True)
def breadcrumb_schema(context):
    request = context.get("request")
    if not request:
        return ""
    path = request.path.strip("/").split("/")
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": request.build_absolute_uri("/")}]

    position = 2
    current_path = ""
    for part in path:
        if not part:
            continue
        current_path += f"/{part}"
        items.append({
            "@type": "ListItem",
            "position": position,
            "name": part.replace("-", " ").title(),
            "item": request.build_absolute_uri(current_path),
        })
        position += 1

    import json
    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }
    return mark_safe(
        '<script type="application/ld+json">' +
        json.dumps(schema, ensure_ascii=False) +
        "</script>"
    )


@register.simple_tag
def organization_schema():
    import json
    schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Chhohreivung",
        "url": "https://chhohreivung.com",
        "logo": "https://chhohreivung.com/static/images/logo.png",
        "description": "Mizo Tech News - Technology news in Mizo language",
        "foundingDate": "2024",
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "general",
            "email": "contact@chhohreivung.com"
        },
        "sameAs": [
            "https://facebook.com/chhohreivung",
            "https://twitter.com/chhohreivung",
            "https://instagram.com/chhohreivung"
        ]
    }
    return mark_safe(
        '<script type="application/ld+json">' +
        json.dumps(schema, ensure_ascii=False, indent=2) +
        "</script>"
    )
