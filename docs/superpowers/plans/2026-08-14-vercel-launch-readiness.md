# Vercel Launch Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the existing Django portfolio safe, discoverable, testable, and documented for Vercel deployment.

**Architecture:** Keep the conventional database-free Django project and use Vercel's native zero-configuration Django integration. One environment-aware settings module provides safe local behavior and fail-closed Vercel behavior; shared template context supplies absolute metadata; small server-rendered routes provide discovery and error responses; Vercel configuration is limited to response headers.

**Tech Stack:** Python 3.12, Django 5.2 LTS, Django templates, custom CSS, vanilla JavaScript, Vercel Python Functions, GitHub Actions

**Spec:** `docs/superpowers/specs/2026-08-14-vercel-launch-readiness-design.md`

## Global Constraints

- Use Vercel's native Django integration; do not add Gunicorn, WhiteNoise, an `api/` wrapper, build commands, or routing rewrites.
- Keep Python 3.12, Django 5.2, `requirements.txt`, the database-free architecture, and the read-only runtime assumption.
- Derive the canonical origin from `SITE_URL`, then `VERCEL_PROJECT_PRODUCTION_URL`, then the local development origin.
- Require `DJANGO_SECRET_KEY` whenever `VERCEL` is set and never commit a production secret.
- Preserve the current curated content, confidentiality boundary, local assets, semantic HTML, keyboard behavior, reduced-motion behavior, and 320 CSS-pixel minimum width.
- Use a strict CSP without `unsafe-inline` or third-party runtime origins.
- Do not add JSON-LD, a custom domain, analytics, cookies, a contact form, accounts, a CMS, a database, durable uploads, or a résumé download.
- Follow strict TDD for observable application behavior. Configuration and human documentation are verified by their real consumers or syntax/check commands, not by source-text assertions.
- Preserve unrelated and pre-existing working-tree changes. Stage only the files named by each task.

---

### Task 1: Private-file protection and Vercel-aware settings

**Files:**
- Modify: `.gitignore`
- Modify: `portfolio/settings.py`
- Create: `website/tests/test_settings.py`

**Interfaces:**
- Consumes: Vercel variables `VERCEL`, `VERCEL_PROJECT_PRODUCTION_URL`; application variables `DJANGO_SECRET_KEY`, optional `SITE_URL`, optional `DJANGO_ALLOWED_HOSTS`.
- Produces: `settings.IS_VERCEL: bool`, `settings.SITE_URL: str`, production-safe `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, middleware, static, proxy, HTTPS, cookie, HSTS, referrer, and framing settings.

- [ ] **Step 1: Write failing settings behavior tests**

Create `website/tests/test_settings.py` with subprocess probes so each case imports a fresh Django settings object:

```python
import json
import os
import subprocess
import sys

from django.conf import settings
from django.test import SimpleTestCase


class DeploymentSettingsTests(SimpleTestCase):
    @staticmethod
    def _probe(expression, **overrides):
        environment = os.environ.copy()
        for name in (
            "VERCEL",
            "VERCEL_PROJECT_PRODUCTION_URL",
            "DJANGO_SECRET_KEY",
            "DJANGO_ALLOWED_HOSTS",
            "SITE_URL",
        ):
            environment.pop(name, None)
        environment.update(overrides)
        environment["DJANGO_SETTINGS_MODULE"] = "portfolio.settings"
        return subprocess.run(
            [sys.executable, "-c", expression],
            capture_output=True,
            text=True,
            env=environment,
            timeout=10,
        )

    def test_local_settings_remain_local_and_http(self):
        result = self._probe(
            "import json; from django.conf import settings; "
            "print(json.dumps({'debug': settings.DEBUG, 'url': settings.SITE_URL, "
            "'redirect': settings.SECURE_SSL_REDIRECT}))"
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            {"debug": True, "url": "http://127.0.0.1:8000", "redirect": False},
        )

    def test_vercel_settings_fail_closed_without_secret(self):
        result = self._probe("from django.conf import settings; print(settings.SECRET_KEY)", VERCEL="1")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DJANGO_SECRET_KEY", result.stderr)

    def test_vercel_settings_derive_secure_origin_and_hosts(self):
        result = self._probe(
            "import json; from django.conf import settings; "
            "print(json.dumps({'debug': settings.DEBUG, 'url': settings.SITE_URL, "
            "'hosts': settings.ALLOWED_HOSTS, 'redirect': settings.SECURE_SSL_REDIRECT, "
            "'proxy': settings.SECURE_PROXY_SSL_HEADER, 'hsts': settings.SECURE_HSTS_SECONDS}))",
            VERCEL="1",
            DJANGO_SECRET_KEY="test-only-secret-key-with-more-than-fifty-unique-characters-1234567890",
            VERCEL_PROJECT_PRODUCTION_URL="norman-portfolio.vercel.app",
            DJANGO_ALLOWED_HOSTS="portfolio.example.com, www.portfolio.example.com",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        values = json.loads(result.stdout)
        self.assertFalse(values["debug"])
        self.assertEqual(values["url"], "https://norman-portfolio.vercel.app")
        self.assertIn(".vercel.app", values["hosts"])
        self.assertIn("norman-portfolio.vercel.app", values["hosts"])
        self.assertIn("portfolio.example.com", values["hosts"])
        self.assertTrue(values["redirect"])
        self.assertEqual(values["proxy"], ["HTTP_X_FORWARDED_PROTO", "https"])
        self.assertEqual(values["hsts"], 63_072_000)

    def test_explicit_site_url_overrides_vercel_origin(self):
        result = self._probe(
            "from django.conf import settings; print(settings.SITE_URL)",
            VERCEL="1",
            DJANGO_SECRET_KEY="test-only-secret-key-with-more-than-fifty-unique-characters-1234567890",
            VERCEL_PROJECT_PRODUCTION_URL="norman-portfolio.vercel.app",
            SITE_URL="https://www.example.com/",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "https://www.example.com")

    def test_private_candidate_instructions_are_git_ignored(self):
        result = subprocess.run(
            ["git", "check-ignore", "-q", "CLAUDE.md"],
            cwd=settings.BASE_DIR,
            timeout=10,
        )

        self.assertEqual(result.returncode, 0)
```

The production change that makes these tests pass is environment-aware settings; hard-coded local settings must fail the new assertions.

- [ ] **Step 2: Run settings tests to verify RED**

Run:

```bash
.venv/bin/python manage.py test website.tests.test_settings -v 2
```

Expected: failures because `SITE_URL`, `IS_VERCEL`, HTTPS controls, fail-closed
secret handling, and the `CLAUDE.md` ignore do not exist.

- [ ] **Step 3: Implement the minimal environment-aware settings**

Replace the local-only settings preamble and add the standard middleware/production controls in `portfolio/settings.py`:

```python
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
```

Keep the current applications/templates and add:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

WSGI_APPLICATION = "portfolio.wsgi.application"
STATIC_URL = "/static/"

SECURE_SSL_REDIRECT = IS_VERCEL
SECURE_PROXY_SSL_HEADER = (
    ("HTTP_X_FORWARDED_PROTO", "https") if IS_VERCEL else None
)
SECURE_HSTS_SECONDS = 63_072_000 if IS_VERCEL else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
CSRF_COOKIE_SECURE = IS_VERCEL
SESSION_COOKIE_SECURE = IS_VERCEL
X_FRAME_OPTIONS = "DENY"
```

- [ ] **Step 4: Add the exact private-file ignore**

Append `CLAUDE.md` inside the existing `# Private source materials` block in `.gitignore`. Verify the real Git consumer:

```bash
git check-ignore -v CLAUDE.md
```

Expected: `.gitignore` identifies `CLAUDE.md` as ignored.

- [ ] **Step 5: Verify local and production settings GREEN**

Run:

```bash
.venv/bin/python manage.py test website.tests.test_settings -v 2
.venv/bin/python manage.py check
VERCEL=1 \
DJANGO_SECRET_KEY=test-only-secret-key-with-more-than-fifty-unique-characters-1234567890 \
VERCEL_PROJECT_PRODUCTION_URL=norman-portfolio.vercel.app \
.venv/bin/python manage.py check --deploy
```

Expected: tests pass and both checks report no issues or warnings.

- [ ] **Step 6: Commit Task 1**

```bash
git add .gitignore portfolio/settings.py website/tests/test_settings.py
git commit -m "feat: secure Vercel runtime settings"
```

---

### Task 2: Canonical and social metadata

**Files:**
- Create: `website/context_processors.py`
- Create: `website/tests/test_metadata.py`
- Modify: `portfolio/settings.py`
- Modify: `website/views.py`
- Modify: `website/templates/website/base.html`

**Interfaces:**
- Consumes: `settings.SITE_URL`, `SITE`, request path, case-study title/summary.
- Produces: `site_metadata(request) -> dict` with `site`, `site_url`, `canonical_url`, `meta_title`, `meta_description`, `social_image_url`, `social_image_alt`; per-view overrides for `meta_title` and `meta_description`.

- [ ] **Step 1: Write failing metadata tests**

Create `website/tests/test_metadata.py`:

```python
from django.test import SimpleTestCase, override_settings
from django.urls import reverse


@override_settings(SITE_URL="https://norman-portfolio.vercel.app")
class MetadataTests(SimpleTestCase):
    def test_primary_pages_render_absolute_canonical_and_social_metadata(self):
        cases = (
            (
                "website:home",
                "Norman Hoang · Quantitative Developer",
                "Quantitative Developer specializing in model implementation, "
                "regulatory analytics, and production-scale data engineering for banking.",
            ),
            (
                "website:experience",
                "Experience · Norman Hoang",
                "Professional experience in quantitative finance, model implementation, "
                "risk analytics, and production-scale data engineering.",
            ),
            (
                "website:case_studies",
                "Case Studies · Norman Hoang",
                "Case studies in financial risk calibration, quantitative platform "
                "engineering, model implementation, and production-scale data engineering.",
            ),
            (
                "website:contact",
                "Contact · Norman Hoang",
                "Contact Norman Hoang about quantitative development, risk and pricing "
                "systems, and banking technology.",
            ),
        )
        for route_name, title, description in cases:
            route = reverse(route_name)
            response = self.client.get(f"{route}?source=test")
            body = response.content.decode()
            with self.subTest(route_name=route_name):
                self.assertIn(f'<link rel="canonical" href="https://norman-portfolio.vercel.app{route}">', body)
                self.assertIn(f'<meta property="og:title" content="{title}">', body)
                self.assertIn(f'<meta name="description" content="{description}">', body)
                self.assertIn('<meta name="twitter:card" content="summary_large_image">', body)
                self.assertIn(
                    'https://norman-portfolio.vercel.app/static/website/img/social-card.png',
                    body,
                )
                self.assertNotIn("?source=test", body)

    def test_case_detail_uses_case_title_summary_and_absolute_url(self):
        route = reverse(
            "website:case_study_detail", kwargs={"slug": "spark-python-modernization"}
        )
        response = self.client.get(route)

        self.assertContains(response, '<meta property="og:type" content="article">', html=True)
        self.assertContains(response, "Spark and Python Quant Platform Modernization")
        self.assertContains(
            response,
            '<meta name="description" content="Modernizing shared quantitative '
            'tooling and the environment used to develop and run it across Global '
            'Risk Analytics.">',
            html=True,
        )
        self.assertContains(
            response,
            f'<meta property="og:url" content="https://norman-portfolio.vercel.app{route}">',
            html=True,
        )
```

- [ ] **Step 2: Run metadata tests to verify RED**

Run:

```bash
.venv/bin/python manage.py test website.tests.test_metadata -v 2
```

Expected: failures because canonical/Open Graph/Twitter tags and metadata context do not exist.

- [ ] **Step 3: Add shared metadata context**

Create `website/context_processors.py`:

```python
from django.conf import settings
from django.templatetags.static import static

from .content import SITE


def site_metadata(request):
    site_url = settings.SITE_URL.rstrip("/")
    return {
        "site": SITE,
        "site_url": site_url,
        "canonical_url": f"{site_url}{request.path}",
        "meta_title": f"{SITE['name']} · Quantitative Developer",
        "meta_description": SITE["supporting_line"],
        "meta_type": "website",
        "social_image_url": f"{site_url}{static('website/img/social-card.png')}",
        "social_image_alt": (
            "Norman Hoang, Quantitative Developer — Risk, Pricing, and Model Implementation"
        ),
    }
```

Add `"website.context_processors.site_metadata"` after the request context processor in `portfolio/settings.py`.

- [ ] **Step 4: Add page-specific view metadata**

Add only `meta_title`, `meta_description`, and detail-page `meta_type` to the existing view contexts in `website/views.py`. Use these exact title/description pairs:

```python
(
    "Norman Hoang · Quantitative Developer",
    "Quantitative Developer specializing in model implementation, regulatory "
    "analytics, and production-scale data engineering for banking.",
)
(
    "Experience · Norman Hoang",
    "Professional experience in quantitative finance, model implementation, risk "
    "analytics, and production-scale data engineering.",
)
(
    "Case Studies · Norman Hoang",
    "Case studies in financial risk calibration, quantitative platform engineering, "
    "model implementation, and production-scale data engineering.",
)
(
    "Contact · Norman Hoang",
    "Contact Norman Hoang about quantitative development, risk and pricing systems, "
    "and banking technology.",
)
(f"{study['title']} · Norman Hoang", study["summary"])
```

For detail pages set `meta_type` to `"article"`.

- [ ] **Step 5: Render shared metadata in the base template**

In `website/templates/website/base.html`, change the title block fallback to
`{{ meta_title }}` so error templates receive their metadata title, preserve all
existing child-template overrides, and replace the shared description with:

```html
<title>{% block title %}{{ meta_title }}{% endblock %}</title>
<meta name="description" content="{{ meta_description }}">
<link rel="canonical" href="{{ canonical_url }}">
<meta property="og:site_name" content="{{ site.name }}">
<meta property="og:type" content="{{ meta_type }}">
<meta property="og:title" content="{{ meta_title }}">
<meta property="og:description" content="{{ meta_description }}">
<meta property="og:url" content="{{ canonical_url }}">
<meta property="og:image" content="{{ social_image_url }}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{{ social_image_alt }}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{ meta_title }}">
<meta name="twitter:description" content="{{ meta_description }}">
<meta name="twitter:image" content="{{ social_image_url }}">
<meta name="twitter:image:alt" content="{{ social_image_alt }}">
```

- [ ] **Step 6: Verify metadata GREEN**

Run:

```bash
.venv/bin/python manage.py test website.tests.test_metadata website.tests.test_pages -v 2
```

Expected: metadata and existing rendered-page tests pass.

- [ ] **Step 7: Commit Task 2**

```bash
git add portfolio/settings.py website/context_processors.py website/views.py website/templates/website/base.html website/tests/test_metadata.py
git commit -m "feat: add canonical social metadata"
```

---

### Task 3: Branded social preview asset

**Files:**
- Create: `website/static/website/img/social-card.svg`
- Create: `website/static/website/img/social-card.png`
- Modify: `website/tests/test_static_assets.py`

**Interfaces:**
- Consumes: approved palette and risk-surface visual language.
- Produces: discoverable 1200×630 `social-card.png` plus editable SVG source.

- [ ] **Step 1: Write the failing static-asset test**

Extend `StaticAssetTests` in `website/tests/test_static_assets.py`:

```python
def test_social_card_is_discoverable_png_with_share_dimensions(self):
    image_path = self._static_path("website/img/social-card.png")
    image_data = image_path.read_bytes()

    self.assertEqual(image_data[:8], b"\x89PNG\r\n\x1a\n")
    self.assertEqual(image_data[12:16], b"IHDR")
    self.assertEqual(struct.unpack(">II", image_data[16:24]), (1200, 630))
    self.assertIsNotNone(finders.find("website/img/social-card.svg"))
```

Also add both social-card paths to `test_required_static_assets_are_discoverable`.

- [ ] **Step 2: Run the focused test to verify RED**

Run:

```bash
.venv/bin/python manage.py test website.tests.test_static_assets.StaticAssetTests.test_social_card_is_discoverable_png_with_share_dimensions -v 2
```

Expected: failure because neither social-card asset exists.

- [ ] **Step 3: Create the editable SVG source**

Create a 1200×630 SVG in `website/static/website/img/social-card.svg` using only these brand values and literal copy:

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#F5F7FA"/>
  <g fill="none" stroke="#D5DCE5" stroke-width="2" opacity="0.75">
    <path d="M690 390C785 285 875 330 950 235C1018 150 1095 176 1225 92"/>
    <path d="M676 447C790 350 882 388 972 297C1041 227 1110 237 1231 166"/>
    <path d="M733 507C842 433 925 454 1011 385C1081 329 1145 330 1240 291"/>
  </g>
  <path d="M680 472C794 385 890 421 978 331C1050 258 1112 274 1228 205"
        fill="none" stroke="#2457C5" stroke-width="4" stroke-dasharray="12 10"/>
  <circle cx="1060" cy="269" r="8" fill="#B5683A"/>
  <text x="92" y="104" fill="#B5683A" font-family="Arial, sans-serif"
        font-size="18" font-weight="700" letter-spacing="4">QUANTITATIVE FINANCE · ENGINEERING</text>
  <text x="88" y="226" fill="#14213D" font-family="Georgia, serif"
        font-size="72" font-weight="700">Norman Hoang</text>
  <text x="92" y="310" fill="#14213D" font-family="Georgia, serif"
        font-size="48" font-weight="700">Quantitative Developer</text>
  <line x1="92" y1="368" x2="608" y2="368" stroke="#14213D" stroke-width="3"/>
  <text x="92" y="425" fill="#5C6675" font-family="Arial, sans-serif"
        font-size="25" letter-spacing="1">Risk · Pricing · Model Implementation</text>
</svg>
```

- [ ] **Step 4: Render the SVG to the committed PNG**

Use a local Chromium/Chrome headless screenshot at the exact viewport, writing the binary asset directly:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --hide-scrollbars \
  --window-size=1200,630 --force-device-scale-factor=1 \
  --screenshot=website/static/website/img/social-card.png \
  "file://$PWD/website/static/website/img/social-card.svg"
```

If Chrome adds viewport chrome or reports a size other than 1200×630, render the SVG through the existing CDP screenshot harness with an explicit `(0, 0, 1200, 630)` clip. Do not resize or fabricate the PNG dimensions in a test.

- [ ] **Step 5: Verify and visually inspect the asset**

Run:

```bash
.venv/bin/python manage.py test website.tests.test_static_assets.StaticAssetTests.test_social_card_is_discoverable_png_with_share_dimensions -v 2
```

Inspect both SVG and PNG. Confirm exact copy, no clipping, no unintended browser margin, correct colors, and readable hierarchy.

- [ ] **Step 6: Commit Task 3**

```bash
git add website/static/website/img/social-card.svg website/static/website/img/social-card.png website/tests/test_static_assets.py
git commit -m "feat: add social preview card"
```

---

### Task 4: Robots and sitemap discovery routes

**Files:**
- Create: `website/templates/website/robots.txt`
- Create: `website/templates/website/sitemap.xml`
- Modify: `website/urls.py`
- Modify: `website/views.py`
- Modify: `website/tests/test_routes.py`

**Interfaces:**
- Consumes: `settings.SITE_URL`, named public routes, `CASE_STUDIES` slugs.
- Produces: named views/routes `robots_txt` at `/robots.txt` and `sitemap_xml` at `/sitemap.xml`.

- [ ] **Step 1: Write failing discovery-route tests**

Add to `PublicRouteTests` in `website/tests/test_routes.py`:

```python
@override_settings(SITE_URL="https://norman-portfolio.vercel.app")
def test_robots_points_to_absolute_sitemap(self):
    response = self.client.get("/robots.txt")

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
    self.assertContains(response, "User-agent: *")
    self.assertContains(response, "Allow: /")
    self.assertContains(
        response, "Sitemap: https://norman-portfolio.vercel.app/sitemap.xml"
    )

@override_settings(SITE_URL="https://norman-portfolio.vercel.app")
def test_sitemap_contains_every_public_route_once(self):
    response = self.client.get("/sitemap.xml")
    expected_paths = [
        reverse("website:home"),
        reverse("website:experience"),
        reverse("website:case_studies"),
        reverse("website:contact"),
        *[
            reverse("website:case_study_detail", kwargs={"slug": slug})
            for slug in (
                "risk-calibration",
                "spark-python-modernization",
                "group-lasso",
                "oracle-trino",
            )
        ],
    ]

    self.assertEqual(response.status_code, 200)
    self.assertTrue(response["Content-Type"].startswith("application/xml"))
    body = response.content.decode()
    for path in expected_paths:
        self.assertEqual(
            body.count(
                f"<loc>https://norman-portfolio.vercel.app{path}</loc>"
            ),
            1,
        )
```

Import `override_settings` alongside `SimpleTestCase`.

- [ ] **Step 2: Run route tests to verify RED**

Run:

```bash
.venv/bin/python manage.py test website.tests.test_routes.PublicRouteTests.test_robots_points_to_absolute_sitemap website.tests.test_routes.PublicRouteTests.test_sitemap_contains_every_public_route_once -v 2
```

Expected: 404 failures because discovery routes do not exist.

- [ ] **Step 3: Add the templates and minimal views**

Create `website/templates/website/robots.txt`:

```text
User-agent: *
Allow: /
Sitemap: {{ site_url }}/sitemap.xml
```

Create `website/templates/website/sitemap.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  {% for url in urls %}<url><loc>{{ url }}</loc></url>{% endfor %}
</urlset>
```

Add views in `website/views.py`:

```python
from django.conf import settings
from django.urls import reverse


def robots_txt(request):
    return render(
        request,
        "website/robots.txt",
        content_type="text/plain; charset=utf-8",
    )


def sitemap_xml(request):
    paths = (
        reverse("website:home"),
        reverse("website:experience"),
        reverse("website:case_studies"),
        reverse("website:contact"),
        *(
            reverse("website:case_study_detail", kwargs={"slug": study["slug"]})
            for study in CASE_STUDIES
        ),
    )
    return render(
        request,
        "website/sitemap.xml",
        {"urls": tuple(f"{settings.SITE_URL}{path}" for path in paths)},
        content_type="application/xml",
    )
```

Register exact routes before the case-study slug route in `website/urls.py`:

```python
path("robots.txt", views.robots_txt, name="robots_txt"),
path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
```

- [ ] **Step 4: Verify discovery routes GREEN**

Run:

```bash
.venv/bin/python manage.py test website.tests.test_routes -v 2
```

Expected: all route tests pass.

- [ ] **Step 5: Commit Task 4**

```bash
git add website/urls.py website/views.py website/templates/website/robots.txt website/templates/website/sitemap.xml website/tests/test_routes.py
git commit -m "feat: publish robots and sitemap"
```

---

### Task 5: Branded 404 and 500 responses

**Files:**
- Create: `website/templates/404.html`
- Create: `website/templates/500.html`
- Modify: `portfolio/urls.py`
- Modify: `website/views.py`
- Modify: `website/tests/test_pages.py`

**Interfaces:**
- Consumes: shared base template, `SITE`, metadata context.
- Produces: `page_not_found(request, exception)` and `server_error(request)` with status 404 and 500; project `handler404` and `handler500` registrations.

- [ ] **Step 1: Write failing error-response tests**

Add `RequestFactory` and `override_settings` imports and these tests to `RenderedPageTests`:

```python
@override_settings(DEBUG=False)
def test_unknown_page_uses_branded_safe_404(self):
    response = self.client.get("/missing-page/")

    self.assertEqual(response.status_code, 404)
    self.assertContains(response, "Page not found", status_code=404)
    self.assertContains(response, 'href="/"', status_code=404)
    self.assertNotContains(response, "Traceback", status_code=404)

def test_server_error_handler_uses_branded_safe_500(self):
    from website.views import server_error

    response = server_error(RequestFactory().get("/failed/"))

    self.assertEqual(response.status_code, 500)
    self.assertContains(response, "Page unavailable", status_code=500)
    self.assertContains(response, 'href="/"', status_code=500)
    self.assertNotContains(response, "Traceback", status_code=500)
```

- [ ] **Step 2: Run focused tests to verify RED**

Run:

```bash
.venv/bin/python manage.py test website.tests.test_pages.RenderedPageTests.test_unknown_page_uses_branded_safe_404 website.tests.test_pages.RenderedPageTests.test_server_error_handler_uses_branded_safe_500 -v 2
```

Expected: the 404 uses Django's default response and `server_error` is missing.

- [ ] **Step 3: Add minimal error handlers and templates**

Add to `website/views.py`:

```python
def page_not_found(request, exception):
    return render(
        request,
        "404.html",
        {
            "meta_title": "Page not found · Norman Hoang",
            "meta_description": "The requested portfolio page could not be found.",
        },
        status=404,
    )


def server_error(request):
    return render(
        request,
        "500.html",
        {
            "meta_title": "Page unavailable · Norman Hoang",
            "meta_description": "The portfolio page could not be loaded.",
        },
        status=500,
    )
```

Register in `portfolio/urls.py`:

```python
handler404 = "website.views.page_not_found"
handler500 = "website.views.server_error"
```

Create `website/templates/404.html` and `website/templates/500.html` extending `website/base.html`. Use a `page-header` with eyebrow `404` or `500`, the exact tested heading, one neutral sentence, and a `Back home` link. Do not render exception content.

- [ ] **Step 4: Verify error pages GREEN**

Run:

```bash
.venv/bin/python manage.py test website.tests.test_pages -v 2
```

Expected: all rendered-page tests pass.

- [ ] **Step 5: Commit Task 5**

```bash
git add portfolio/urls.py website/views.py website/templates/404.html website/templates/500.html website/tests/test_pages.py
git commit -m "feat: add branded error pages"
```

---

### Task 6: Vercel response-security configuration

**Files:**
- Create: `vercel.json`
- Create: `website/tests/test_vercel_config.py`

**Interfaces:**
- Consumes: all-local runtime asset policy.
- Produces: Vercel-wide CSP, nosniff, frame-denial, referrer, and permissions headers with no build or routing configuration.

- [ ] **Step 1: Write the failing Vercel configuration behavior test**

Create `website/tests/test_vercel_config.py`:

```python
import json
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class VercelConfigurationTests(SimpleTestCase):
    def test_vercel_config_applies_strict_headers_without_routing_or_builds(self):
        config_path = Path(settings.BASE_DIR) / "vercel.json"
        self.assertTrue(config_path.exists())
        config = json.loads(config_path.read_text())

        self.assertNotIn("builds", config)
        self.assertNotIn("routes", config)
        self.assertNotIn("rewrites", config)
        self.assertEqual(len(config["headers"]), 1)
        self.assertEqual(config["headers"][0]["source"], "/(.*)")
        headers = {
            item["key"]: item["value"] for item in config["headers"][0]["headers"]
        }
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(headers["X-Frame-Options"], "DENY")
        self.assertEqual(
            headers["Referrer-Policy"], "strict-origin-when-cross-origin"
        )
        csp = headers["Content-Security-Policy"]
        self.assertIn("default-src 'self'", csp)
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertNotIn("unsafe-inline", csp)
        self.assertNotIn("http:", csp)
        self.assertNotIn("https:", csp)
```

This invokes the JSON parser and asserts the behavior Vercel consumes rather than grepping source text.

- [ ] **Step 2: Run the focused test to verify RED**

Run:

```bash
.venv/bin/python manage.py test website.tests.test_vercel_config -v 2
```

Expected: failure because `vercel.json` is missing.

- [ ] **Step 3: Add the minimal header-only Vercel configuration**

Create `vercel.json`:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; form-action 'self'; img-src 'self' data:; font-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; upgrade-insecure-requests"
        },
        {"key": "X-Content-Type-Options", "value": "nosniff"},
        {"key": "X-Frame-Options", "value": "DENY"},
        {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
        {
          "key": "Permissions-Policy",
          "value": "camera=(), microphone=(), geolocation=()"
        }
      ]
    }
  ]
}
```

- [ ] **Step 4: Verify configuration GREEN**

Run:

```bash
.venv/bin/python manage.py test website.tests.test_vercel_config -v 2
python -m json.tool vercel.json >/dev/null
```

Expected: focused test and JSON parser pass.

- [ ] **Step 5: Commit Task 6**

```bash
git add vercel.json website/tests/test_vercel_config.py
git commit -m "feat: add Vercel security headers"
```

---

### Task 7: GitHub Actions continuous verification

**Files:**
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: Python 3.12, `requirements.txt`, Django checks/tests/staticfiles, Node syntax check, production Vercel variables.
- Produces: one `verify` workflow job on pushes and pull requests.

- [ ] **Step 1: Create the workflow**

Create `.github/workflows/ci.yml`:

```yaml
name: Verify

on:
  push:
  pull_request:

jobs:
  verify:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -r requirements.txt
      - name: Verify dependencies
        run: python -m pip check
      - name: Check Django project
        run: python manage.py check
      - name: Run tests
        run: python manage.py test --verbosity 1
      - name: Verify static collection
        run: python manage.py collectstatic --noinput --dry-run
      - name: Check JavaScript syntax
        run: node --check website/static/website/js/site.js
      - name: Check production settings
        env:
          VERCEL: "1"
          DJANGO_SECRET_KEY: test-only-secret-key-with-more-than-fifty-unique-characters-1234567890
          VERCEL_PROJECT_PRODUCTION_URL: norman-portfolio.vercel.app
        run: python manage.py check --deploy
```

This configuration contains no production secret. It is a consumer rather than application behavior, so validate its commands directly instead of adding a source-shape unit test.

- [ ] **Step 2: Run every workflow command locally**

Run:

```bash
.venv/bin/python -m pip check
.venv/bin/python manage.py check
.venv/bin/python manage.py test --verbosity 1
.venv/bin/python manage.py collectstatic --noinput --dry-run
node --check website/static/website/js/site.js
VERCEL=1 \
DJANGO_SECRET_KEY=test-only-secret-key-with-more-than-fifty-unique-characters-1234567890 \
VERCEL_PROJECT_PRODUCTION_URL=norman-portfolio.vercel.app \
.venv/bin/python manage.py check --deploy
```

Expected: every command exits zero; Django checks report no warnings.

- [ ] **Step 3: Validate workflow syntax through its real consumer**

After the branch is pushed, confirm the `Verify` workflow is accepted by GitHub Actions and the `verify` job passes. If pushing remains out of scope in the execution session, report this as the only external verification still pending; do not install a YAML dependency solely to parse one workflow.

- [ ] **Step 4: Commit Task 7**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: verify Django portfolio"
```

---

### Task 8: Current documentation and final browser evidence

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/specs/2026-08-12-resume-website-design.md`
- Modify: `docs/verification/responsive-review.md`

**Interfaces:**
- Consumes: all completed runtime, metadata, discovery, error-page, security, and CI behavior.
- Produces: current setup/deployment documentation and reproducible final verification evidence.

- [ ] **Step 1: Update the original design specification**

Edit `docs/superpowers/specs/2026-08-12-resume-website-design.md` so its current-state sections match the accepted site:

- Contact is `/contact/`, not a homepage closing section.
- The Home proof ledger is `~2B`, `58 → 119`, and `IFRS · CECL · CCAR`.
- The four case studies are risk calibration, Spark/Python modernization, Group Lasso, and Oracle-to-Trino.
- Independent Work contains FinApp and Mathematics of Model Explainability only.
- The working paper description includes XGBoost, SHAP, and feature importance.
- Beyond work and CloudKit are absent.
- Experience includes Leadership & community and the Systems and Signals specialization.
- Vercel launch readiness is in scope via the 2026-08-14 extension spec.

Do not rewrite historical implementation-plan steps; update the design's authoritative requirements and clearly link to the extension spec.

- [ ] **Step 2: Expand README deployment instructions**

Add a `## Deploying to Vercel` section explaining:

1. Import the repository into Vercel with framework auto-detection.
2. Expose Vercel system environment variables.
3. Set `DJANGO_SECRET_KEY` in Production and Preview.
4. Optionally set `SITE_URL` after adding a custom domain.
5. Optionally set exact custom domains in `DJANGO_ALLOWED_HOSTS`.
6. Deploy without a build command or output-directory override.
7. Verify public routes, static assets, security headers, canonical metadata,
   social preview, robots, sitemap, and error pages.

Document that Vercel's deployed filesystem is read-only except ephemeral `/tmp`,
and persistent state would require an external managed store. Update the public
route list with `/robots.txt` and `/sitemap.xml`. Replace the statement that
deployment is out of scope.

- [ ] **Step 3: Run the complete automated gate**

Run:

```bash
set -e
.venv/bin/python -m pip check
.venv/bin/python manage.py check
.venv/bin/python manage.py test --verbosity 1
.venv/bin/python manage.py collectstatic --noinput --dry-run
node --check website/static/website/js/site.js
python -m json.tool vercel.json >/dev/null
VERCEL=1 \
DJANGO_SECRET_KEY=test-only-secret-key-with-more-than-fifty-unique-characters-1234567890 \
VERCEL_PROJECT_PRODUCTION_URL=norman-portfolio.vercel.app \
.venv/bin/python manage.py check --deploy
git diff --check
git check-ignore -q CLAUDE.md
```

Expected: every command exits zero, all tests pass, and both Django checks report no issues or warnings.

- [ ] **Step 4: Run the real-browser matrix**

Start local Django and headless Chrome. Check these HTML routes:

```text
/
/experience/
/case-studies/
/case-studies/risk-calibration/
/case-studies/spark-python-modernization/
/case-studies/group-lasso/
/case-studies/oracle-trino/
/contact/
/missing-page/ with DEBUG=False
```

Check `/robots.txt` and `/sitemap.xml` separately as text/XML. At 320×568,
375×812, 768×1024, and 1440×1200 assert:

- `document.documentElement.scrollWidth <= innerWidth`
- local images decode and fonts load
- no console exceptions, failed requests, or external runtime requests
- mobile menu opens, closes by link, closes with Escape, and restores focus
- reduced motion disables contour animation
- every HTML page renders an absolute production canonical URL and social image
- 404 has the branded heading and correct status

Capture and visually inspect Home, Contact, Case Studies, the Spark/Python detail,
404, and 500 at desktop and mobile sizes. Inspect the 1200×630 social card at
original resolution.

- [ ] **Step 5: Replace responsive-review evidence**

Update `docs/verification/responsive-review.md` with the current date, browser
version, exact route/viewport coverage, automation results, screenshot paths,
visual inspection results, metadata/discovery checks, error-page checks, and any
external verification still pending. Remove stale claims about excluded captures
only when fresh captures provide passing replacement evidence.

- [ ] **Step 6: Commit Task 8**

```bash
git add README.md docs/superpowers/specs/2026-08-12-resume-website-design.md docs/verification/responsive-review.md
git commit -m "docs: document Vercel deployment"
```

- [ ] **Step 7: Final branch verification**

Run:

```bash
git status --short
git log --oneline -10
```

Confirm no task-owned files remain unstaged or uncommitted. Preserve and report
all unrelated pre-existing working-tree changes. Do not deploy, push, or alter
Vercel Project Settings without separate user authorization.
