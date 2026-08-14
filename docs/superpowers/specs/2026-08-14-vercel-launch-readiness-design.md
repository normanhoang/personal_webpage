# Vercel Launch Readiness Design

## Purpose

Prepare the existing Django portfolio for a future Vercel deployment without
changing its curated content strategy or server-rendered architecture. The work
must close the current privacy risk, provide production-safe Django settings,
add search and social metadata, establish continuous verification, add branded
error handling, and bring repository documentation in line with the current
site.

This design extends the original resume-website design. It does not introduce a
database, CMS, contact form, analytics, accounts, or a frontend build system.

## Accepted Decisions

- Deploy with Vercel's native zero-configuration Django integration.
- Keep the conventional root `manage.py` and `portfolio/wsgi.py` layout.
- Keep Python 3.12 and `requirements.txt`.
- Do not add Gunicorn, WhiteNoise, an `api/` adapter, build commands, or routing
  rewrites.
- Derive canonical URLs from `VERCEL_PROJECT_PRODUCTION_URL`, while allowing a
  future explicit `SITE_URL` override for a custom domain.
- Use a headshot-free 1200×630 social card based on the existing editorial risk
  surface.
- Keep a strict Content Security Policy and omit inline JSON-LD.
- Keep the application database-free and compatible with Vercel's read-only
  deployed filesystem.

The supporting primary-source research is recorded in
`docs/research/vercel-django-deployment.md`.

## Privacy Boundary

Add `CLAUDE.md` to the exact private-source entries in `.gitignore`. It contains
candidate and job-search details that must not be published with the portfolio.
Do not use a broad ignore pattern that could hide a future public project
instruction file.

The existing confidentiality tests remain in force. Production HTML must not
expose the phone number, compensation constraints, work-authorization details,
relocation constraints, or internal infrastructure and incident details.

## Vercel and Django Runtime

Vercel will detect the existing Django application through the root
`manage.py`, the Django settings module, and `portfolio/wsgi.py`. Add
`WSGI_APPLICATION = "portfolio.wsgi.application"` so the production entry point
is explicit.

The single settings module remains small and environment-aware:

- Local development uses the existing local-only secret, `DEBUG=True`, the
  localhost allowlist, and HTTP.
- A truthy `VERCEL` environment variable activates production behavior.
- Vercel execution requires `DJANGO_SECRET_KEY`; settings must fail closed with
  a clear configuration error when it is missing.
- `DEBUG=False` on Vercel.
- `ALLOWED_HOSTS` includes localhost/test hosts, `.vercel.app`, the host parsed
  from `VERCEL_PROJECT_PRODUCTION_URL`, and exact comma-separated hosts supplied
  through optional `DJANGO_ALLOWED_HOSTS`.
- `SITE_URL` uses an explicit `SITE_URL` environment variable when present,
  otherwise `https://` plus `VERCEL_PROJECT_PRODUCTION_URL`, otherwise the local
  development origin. Normalize it by removing a trailing slash.
- `STATIC_URL` is absolute (`/static/`) and `STATIC_ROOT` remains configured so
  Vercel can collect and publish assets through its CDN.

Enable the minimal standard middleware required for this public site:

1. `SecurityMiddleware`
2. `CommonMiddleware`
3. `CsrfViewMiddleware`
4. `XFrameOptionsMiddleware`

On Vercel, trust the documented `X-Forwarded-Proto` header, redirect HTTP to
HTTPS, use secure CSRF/session-cookie settings, deny framing, and use a strict
referrer policy. Match Vercel's two-year HSTS duration without enabling preload
or `includeSubDomains`.

## Response Security Policy

Add a root `vercel.json` containing response headers only. It must not contain
build configuration or routing rewrites. Apply these policies to all paths:

- A self-only Content Security Policy covering scripts, styles, fonts, images,
  and connections; block objects and framing; restrict base and form targets;
  upgrade insecure requests.
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- A restrictive `Permissions-Policy` for camera, microphone, and geolocation.

The site currently uses only local CSS, JavaScript, images, and fonts and has no
inline executable scripts, so this policy must not require `unsafe-inline` or
third-party origins. Validate the exact headers on a Vercel Preview before the
Production promotion. The Vercel Preview Toolbar may need to remain disabled
under the strict policy.

## Shared Metadata

Add a small context processor that makes the following values available to all
templates, including error pages:

- `site`
- normalized production `site_url`
- request-derived canonical URL without query parameters
- default page title and description
- absolute social-card URL

Individual views override only the page title and description. Use the case
study title and summary for detail pages. The shared `<head>` renders:

- unique `<title>` and meta description
- canonical link
- Open Graph title, description, type, URL, image, image dimensions, and image
  alternative text
- Twitter large-image card metadata

The canonical origin on Preview deployments remains the Production Vercel URL,
not the changing deployment-specific `VERCEL_URL`.

## Social Preview Asset

Create a 1200×630 PNG social card and retain a code-native SVG source. The card
uses the existing ledger-white background, ink navy typography, cobalt signal,
copper annotation, and risk-surface contour. It contains exactly:

- `Norman Hoang`
- `Quantitative Developer`
- `Risk · Pricing · Model Implementation`

It contains no headshot, employer logo, or unsupported claim. Tests verify the
PNG signature, dimensions, staticfiles discovery, and rendered absolute URL.

## Discovery Routes

Add two named, server-rendered public routes:

- `/robots.txt` with `text/plain; charset=utf-8`
- `/sitemap.xml` with `application/xml`

`robots.txt` allows crawling and points to the absolute production sitemap.
The sitemap contains the Home, Experience, Case Studies, Contact, and every
case-study detail URL. It omits fabricated modification dates and priorities.

Vercel's Preview `X-Robots-Tag: noindex` behavior remains a deployment concern;
the application does not attempt to infer or duplicate that header.

## Error Handling

Add branded `404.html` and `500.html` templates using the existing navigation,
typography, footer, and restrained tone. The 404 page explains that the page was
not found and links home. The 500 page states that the page could not be loaded
and links home. Neither page exposes exception details or internal state.

Register explicit Django 404 and 500 handlers so both pages receive the shared
site and metadata context. Responses retain their correct status codes.

## Continuous Integration

Add `.github/workflows/ci.yml` for pushes and pull requests. The workflow uses
Python 3.12 and performs:

1. dependency installation from `requirements.txt`
2. `python -m pip check`
3. `python manage.py check`
4. `python manage.py test`
5. `python manage.py collectstatic --noinput --dry-run`
6. JavaScript syntax validation with Node
7. `python manage.py check --deploy` under production-equivalent Vercel
   environment variables and a strong non-production test secret

The deployment check must complete without warnings. CI must not contain a real
production secret or domain.

## Documentation

Update the original design specification so it describes the current product:

- Contact is a dedicated page.
- There are four case studies, including Spark and Python platform
  modernization.
- The current proof ledger, capability groups, education specialization, and
  Leadership & community section are authoritative.
- CloudKit Reliability Investigation and Beyond work are removed.
- The working paper mentions XGBoost, SHAP, and feature importance.
- Vercel deployment is no longer out of scope.

Update the README with Vercel's zero-configuration deployment path, required
environment variables, system-variable exposure, local commands, and
post-deployment verification. Document that Vercel storage is read-only except
for ephemeral `/tmp` and that persistent features would require an external
store.

After implementation, replace or append the responsive-review evidence with a
fresh run covering every public route, the new error pages, 320, 375, 768, and
1440 CSS pixels, mobile-menu behavior, reduced motion, overflow, asset loading,
browser errors, and metadata/discovery endpoints.

## Testing Strategy

Use test-driven development for each observable behavior:

- settings tests for local defaults, Vercel fail-closed behavior, derived
  production URL, hosts, and security settings
- rendered-page tests for unique metadata and absolute canonical/social URLs
- route tests for robots, sitemap, and every sitemap location
- error-handler tests for branded content, safe copy, and status codes
- static-asset tests for social-card discovery and 1200×630 PNG dimensions
- privacy protection check proving `CLAUDE.md` is ignored
- configuration tests for the required Vercel security headers and absence of
  builds/rewrites

Run the complete Django suite, local and deployment system checks, static
collection, JavaScript syntax validation, diff checks, and a real-browser route
and viewport matrix before completion.

## Out of Scope

- Choosing or configuring a custom domain
- Executing a Vercel deployment or changing Vercel Project Settings
- Vercel Toolbar CSP exceptions
- Database, durable uploads, filesystem sessions, or generated runtime files
- CMS, contact form, analytics, cookies, accounts, or admin
- Inline JSON-LD
- Resume download
