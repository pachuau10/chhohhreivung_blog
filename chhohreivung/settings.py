import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="django-insecure-change-me-in-production")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config(
    "DJANGO_ALLOWED_HOSTS", default="localhost,127.0.0.1,.vercel.app,chhohhreivung.vercel.app", cast=Csv()
)

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="http://localhost:8000,http://127.0.0.1:8000,https://chhohhreivung.vercel.app",
    cast=Csv(),
)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

SITE_URL = config("SITE_URL", default="http://localhost:8000")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.sites",
    "django.contrib.humanize",
    "ckeditor",
    "cloudinary",
    "cloudinary_storage",
    "blog",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "chhohreivung.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "blog.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "chhohreivung.wsgi.application"

DATABASE_URL = config("DATABASE_URL", default="")

if DATABASE_URL.startswith("postgres"):
    import dj_database_url
    DATABASES = {"default": dj_database_url.config(default=DATABASE_URL, conn_max_age=600)}
    DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}
    DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# --- Static Files (WhiteNoise) ---
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
WHITENOISE_MAX_AGE = 31536000
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG

# --- Media / Cloudinary ---
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": config("CLOUDINARY_CLOUD_NAME", default=""),
    "API_KEY": config("CLOUDINARY_API_KEY", default=""),
    "API_SECRET": config("CLOUDINARY_API_SECRET", default=""),
}

USE_CLOUDINARY = config("USE_CLOUDINARY", default=False, cast=bool)

if USE_CLOUDINARY:
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
else:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

MEDIA_URL = "/media/"
if not USE_CLOUDINARY:
    MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": DEFAULT_FILE_STORAGE},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# --- CKEditor ---
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "full",
        "height": 500,
        "width": "100%",
        "extraPlugins": ",".join([
            "codesnippet",
            "image2",
            "tableresize",
            "uploadimage",
        ]),
        "specialChars": ["Ṭ", "ṭ", "Â", "â", "Ê", "ê", "Î", "î", "Ô", "ô", "Û", "û", "Á", "É", "Í", "Ó", "Ú", "À", "È", "Ì", "Ò", "Ù"],
        "toolbar_Custom": [
            {"name": "document", "items": ["Source", "-", "Save", "NewPage", "Preview", "Print", "-", "Templates"]},
            {"name": "clipboard", "items": ["Cut", "Copy", "Paste", "PasteText", "PasteFromWord", "-", "Undo", "Redo"]},
            {"name": "editing", "items": ["Find", "Replace", "-", "SelectAll", "Scayt"]},
            {"name": "forms", "items": ["Form", "Checkbox", "Radio", "TextField", "Textarea", "Select", "Button"]},
            "/",
            {"name": "basicstyles", "items": ["Bold", "Italic", "Underline", "Strike", "Subscript", "Superscript", "-", "RemoveFormat"]},
            {"name": "paragraph", "items": ["NumberedList", "BulletedList", "-", "Outdent", "Indent", "-", "Blockquote", "CreateDiv", "-", "JustifyLeft", "JustifyCenter", "JustifyRight", "JustifyBlock", "-", "BidiLtr", "BidiRtl", "Language"]},
            {"name": "links", "items": ["Link", "Unlink", "Anchor"]},
            {"name": "insert", "items": ["Image", "Table", "HorizontalRule", "Smiley", "SpecialChar", "PageBreak", "Iframe"]},
            "/",
            {"name": "styles", "items": ["Styles", "Format", "Font", "FontSize"]},
            {"name": "colors", "items": ["TextColor", "BGColor"]},
            {"name": "tools", "items": ["Maximize", "ShowBlocks"]},
            {"name": "about", "items": ["About"]},
        ],
    }
}

# --- Cache ---
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

if not DEBUG:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

# --- Email / SMTP ---
CONTACT_EMAIL = config("CONTACT_EMAIL", default="contact@chhohreivung.com")
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=False, cast=bool)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="Chhohreivung <noreply@chhohreivung.com>")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
