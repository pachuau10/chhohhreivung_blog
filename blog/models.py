from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
import re


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Category Name")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category", args=[self.slug])


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tag", args=[self.slug])


class Article(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]

    title = models.CharField(max_length=255, verbose_name="Title")
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    excerpt = models.TextField(max_length=500, blank=True, verbose_name="Excerpt")
    content = RichTextField(verbose_name="Content")
    featured_image = models.ImageField(
        upload_to="articles/", blank=True, null=True, verbose_name="Featured Image"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="articles"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, default=1)
    views = models.PositiveIntegerField(default=0, editable=False)
    published_at = models.DateTimeField(blank=True, null=True, verbose_name="Published At")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    featured = models.BooleanField(default=False, verbose_name="Featured Article")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="draft"
    )
    meta_title = models.CharField(max_length=70, blank=True, verbose_name="Meta Title")
    meta_description = models.CharField(
        max_length=160, blank=True, verbose_name="Meta Description"
    )
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name="Meta Keywords")

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "published_at"]),
            models.Index(fields=["status", "featured", "published_at"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["category", "status", "published_at"]),
            models.Index(fields=["-views"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while Article.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        if not self.meta_title:
            self.meta_title = self.title[:60]
        if not self.meta_description:
            self.meta_description = self.excerpt[:155] if self.excerpt else self.title[:155]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("article_detail", args=[self.slug])

    def reading_time(self):
        word_count = len(re.findall(r"\w+", self.content))
        minutes = max(1, round(word_count / 200))
        return minutes

    def increment_views(self):
        Article.objects.filter(pk=self.pk).update(views=models.F("views") + 1)


class PageView(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, null=True, blank=True, related_name="page_views"
    )
    path = models.CharField(max_length=500)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-viewed_at"]

    def __str__(self):
        return f"{self.path} @ {self.viewed_at:%Y-%m-%d}"


class Income(models.Model):
    SOURCE_CHOICES = [
        ("adsense", "Google AdSense"),
        ("sponsorship", "Sponsorship"),
        ("affiliate", "Affiliate"),
        ("donation", "Donation"),
        ("other", "Other"),
    ]

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default="adsense")
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Income"

    def __str__(self):
        return f"{self.get_source_display()}: ${self.amount} on {self.date}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.name} - {self.subject[:40]}"

