import os
from pathlib import Path
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parent.parent
IS_VERCEL = bool(os.environ.get("VERCEL"))

if IS_VERCEL:
    SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
    if not SECRET_KEY:
        raise ImproperlyConfigured("DJANGO_SECRET_KEY is required on Vercel")
else:
    SECRET_KEY = "local-development-only-secret-key"

DEBUG = not IS_VERCEL

production_domain = os.environ.get("VERCEL_PROJECT_PRODUCTION_URL", "").strip()
explicit_site_url = os.environ.get("SITE_URL", "").strip()
SITE_URL = (
    explicit_site_url
    or (f"https://{production_domain}" if production_domain else "")
    or "http://127.0.0.1:8000"
).rstrip("/")

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]
if IS_VERCEL:
    ALLOWED_HOSTS.append(".vercel.app")
for candidate in (
    urlsplit(SITE_URL).hostname,
    production_domain,
    *os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(","),
):
    host = (candidate or "").strip()
    if host and host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "website",
]

ROOT_URLCONF = "portfolio.urls"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "website.context_processors.site_metadata",
            ],
        },
    },
]

WSGI_APPLICATION = "portfolio.wsgi.application"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

SECURE_SSL_REDIRECT = IS_VERCEL
SECURE_PROXY_SSL_HEADER = (
    ("HTTP_X_FORWARDED_PROTO", "https") if IS_VERCEL else None
)
SECURE_HSTS_SECONDS = 63_072_000 if IS_VERCEL else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
if IS_VERCEL:
    SILENCED_SYSTEM_CHECKS = ["security.W005", "security.W021"]
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
CSRF_COOKIE_SECURE = IS_VERCEL
SESSION_COOKIE_SECURE = IS_VERCEL
X_FRAME_OPTIONS = "DENY"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
