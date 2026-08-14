# Django 5.2 on Vercel: deployment findings

Research date: 2026-08-14. Sources are limited to official Vercel documentation/examples and Django 5.2 documentation.

## Recommended architecture for this repository

Use Vercel's native Django integration and keep the existing conventional layout:

```text
manage.py
portfolio/
  settings.py
  wsgi.py
requirements.txt
.python-version
```

Vercel added zero-configuration Django support in April 2026. It detects a root `manage.py`, finds the Django settings and WSGI application, and handles the app as a Vercel Function. The official example uses the same structure. An `api/` adapter, catch-all rewrite, custom start command, and routing-oriented `vercel.json` are no longer needed. Explicitly declaring `WSGI_APPLICATION = "portfolio.wsgi.application"` matches the official example and makes the entry point unambiguous. [Vercel zero-configuration Django announcement](https://vercel.com/changelog/zero-configuration-django-support), [official Vercel Django example](https://github.com/vercel/examples/tree/main/python/django)

Keep `requirements.txt`; the Python runtime installs dependencies from it directly. A `pyproject.toml` is optional, not a deployment requirement. Vercel also accepts `pyproject.toml`/`uv.lock` or Pipenv, but adding a second dependency manifest here would create avoidable duplication. The root `.python-version` already pins `3.12`, which Vercel respects. As of the research date, supported runtime versions are 3.12, 3.13, and 3.14, with 3.12 the default; the Python runtime is still documented as Beta. [Vercel Python runtime](https://vercel.com/docs/functions/runtimes/python)

## Static files

Retain:

- `django.contrib.staticfiles`
- an absolute `STATIC_URL`, conventionally `/static/`
- `STATIC_ROOT`

Vercel's Django detector reads the static-files configuration and serves collected static assets through Vercel's CDN. Django independently requires `STATIC_ROOT` for production collection. A separate manual static route or application-level file server is not indicated by the current integration. [Vercel Django template](https://vercel.com/templates/python/django-hello-world), [Vercel zero-configuration announcement](https://vercel.com/changelog/zero-configuration-django-support), [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)

### Gunicorn and WhiteNoise

Do not add either for this Vercel target:

- **Gunicorn:** Vercel invokes the WSGI application inside its Python Function runtime; there is no persistent process or user-defined production start command for Gunicorn to own. Vercel is the production WSGI host in this architecture.
- **WhiteNoise:** Vercel's Django integration publishes static files through its CDN. Serving them again through WSGI would duplicate that responsibility and enlarge the function dependency set.

This is an architecture recommendation, not a Vercel prohibition. Both packages are useful on traditional process hosts, but neither is part of Vercel's current official Django example. [Official Vercel Django example](https://github.com/vercel/examples/tree/main/python/django), [Vercel zero-configuration announcement](https://vercel.com/changelog/zero-configuration-django-support)

## Environment and Django production settings

Configure environment variables in Vercel Project Settings, scoped separately to Production, Preview, and Development. Vercel encrypts configured values at rest; changed variables apply only to new deployments. Do not commit pulled `.env` files. [Vercel environment variables](https://vercel.com/docs/environment-variables)

Recommended application variables:

| Variable | Purpose |
| --- | --- |
| `DJANGO_SECRET_KEY` | A strong, unique production signing key. Fail closed on Vercel if absent. |
| `SITE_URL` | Stable canonical origin, including `https://`, e.g. `https://example.com`. |
| `DJANGO_ALLOWED_HOSTS` | Optional comma-separated exact custom hosts; retain local hosts and `.vercel.app` for local/preview URLs. |

The application should make `DEBUG=False` whenever it is running on Vercel, use a noncommitted production secret, and avoid `ALLOWED_HOSTS = ["*"]`. Django requires a suitable host allowlist with debug disabled; a leading-dot entry such as `.vercel.app` covers Vercel deployment subdomains, while the eventual custom host should be added explicitly. [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/), [Django `ALLOWED_HOSTS`](https://docs.djangoproject.com/en/5.2/ref/settings/#allowed-hosts), [official Vercel Django settings](https://raw.githubusercontent.com/vercel/examples/main/python/django/config/settings.py)

Vercel sends `X-Forwarded-Proto` with the original protocol, normally `https` in production and `http` in development. On Vercel, Django can therefore use:

```python
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
```

This enables correct `request.is_secure()` and safe use of production-only HTTPS settings. Django warns that this header must only be trusted when the proxy is known to overwrite it; Vercel documents that it supplies the header. [Vercel request headers](https://vercel.com/docs/headers/request-headers), [Django `SECURE_PROXY_SSL_HEADER`](https://docs.djangoproject.com/en/5.2/ref/settings/#secure-proxy-ssl-header)

Use Django's `SecurityMiddleware` and `XFrameOptionsMiddleware`; set secure CSRF/session cookies if those cookies are ever emitted, and enable HTTPS redirect only in the Vercel/production environment so local `runserver` remains usable. Vercel already emits `Strict-Transport-Security: max-age=63072000` by default, so an additional Django HSTS value is redundant. HSTS `includeSubDomains`/`preload` should not be enabled casually because Django notes that an incorrect policy can break subdomains for the policy lifetime. [Vercel response headers](https://vercel.com/docs/headers/response-headers), [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/), [Django security settings](https://docs.djangoproject.com/en/5.2/ref/settings/#secure-hsts-seconds)

## CSP and `vercel.json`

Django 5.2 predates Django's built-in CSP middleware. For this static portfolio, a small root `vercel.json` is appropriate **only for response headers**, not builds or routing. Vercel's `headers` configuration can apply a Content Security Policy and related headers to both Function and static responses. The current templates load script, styles, images, and fonts locally and contain no inline script/style, so a restrictive self-only policy is feasible; verify the exact policy in Preview before enforcing it. Vercel notes that its Preview Toolbar may require CSP allowances if the toolbar is used. [Vercel `vercel.json` headers](https://vercel.com/docs/project-configuration/vercel-json#headers), [Vercel Toolbar and CSP](https://vercel.com/docs/vercel-toolbar/managing-toolbar), [Django 5.2 middleware reference](https://docs.djangoproject.com/en/5.2/ref/middleware/)

## Filesystem and Function constraints

Vercel Functions have a read-only deployed filesystem. Only `/tmp` is writable, with up to 500 MB of temporary scratch space; it is not durable application storage. Python function bundles are limited to 500 MB uncompressed and Python dependencies are not tree-shaken automatically. [Vercel runtimes](https://vercel.com/docs/functions/runtimes), [Vercel Python runtime](https://vercel.com/docs/functions/runtimes/python), [Vercel Function limits](https://vercel.com/docs/functions/limitations)

The current database-free, read-only portfolio fits this model. Do not later rely on deployed SQLite, filesystem sessions/cache, uploaded media, or generated local files for durable state. Use an external managed store if persistent state is introduced.

## Custom domain and canonical URL

Add the eventual domain under Vercel Project Settings → Domains (or with the Vercel CLI), then follow the exact DNS records Vercel reports. Vercel provisions TLS after domain verification. If both apex and `www` are attached, select one canonical host and redirect the other in Project Settings to prevent duplicate content. [Vercel custom-domain setup](https://vercel.com/docs/domains/set-up-custom-domain), [Vercel domain redirects](https://vercel.com/docs/domains/working-with-domains/deploying-and-redirecting), [Vercel SSL](https://vercel.com/docs/domains/working-with-ssl)

For HTML canonical links, Open Graph URLs, and the sitemap, prefer an explicit `SITE_URL`. A useful fallback is `https://` plus `VERCEL_PROJECT_PRODUCTION_URL`, which selects the shortest production custom domain (or the production `vercel.app` domain) and remains stable during Preview builds. System variables must be exposed in the project settings for this fallback to exist. Do not use `VERCEL_URL` for canonical metadata because it identifies the individual deployment and changes across previews. [Vercel system environment variables](https://vercel.com/docs/environment-variables/system-environment-variables)

Vercel automatically sends `X-Robots-Tag: noindex` on Preview and outdated Production deployments, reducing duplicate-indexing risk. The application should still publish its own production `robots.txt`, sitemap, per-page metadata, and canonical tags. [Vercel response headers](https://vercel.com/docs/headers/response-headers)

## Verification target

Before deployment, run the normal test suite plus `python manage.py check --deploy` under production-equivalent environment variables. After a Preview deployment, verify page routes, `/static/` responses, CSP/security headers, canonical metadata, `robots.txt`, sitemap contents, the custom 404/500 templates, and that the Production deployment does not receive Vercel's Preview-only `noindex` header. Django explicitly recommends deployment checks and supports root `400.html`, `403.html`, `404.html`, and `500.html` error templates. [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)

## Uncertainties and source precedence

- Some generic Vercel Python-runtime text still describes Django as requiring manual configuration. That predates or has not fully caught up with the framework-specific zero-configuration support announced on 2026-04-09. The current Django documentation, changelog, template, and official example should take precedence.
- Vercel documents Python support as Beta. Recheck supported versions and Django auto-detection before a future runtime upgrade.
- The exact custom domain is not yet known, so `SITE_URL` and the custom `ALLOWED_HOSTS` entry must be supplied at deployment time.
- CSP should be validated against the deployed Preview, particularly if Vercel Toolbar/Comments are enabled.
