# Norman Hoang Resume Website

A focused Django portfolio presenting professional experience and selected case studies.

## Local setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py runserver
```

Open <http://127.0.0.1:8000/>.

## Verification

```bash
python manage.py check
python manage.py test
```

## Public routes

- `/` — Home
- `/experience/` — Experience
- `/case-studies/` — Case Studies
- `/contact/` — Contact
- `/case-studies/risk-calibration/` — Financial Risk Calibration Library
- `/case-studies/spark-python-modernization/` — Spark and Python Quant Platform Modernization
- `/case-studies/group-lasso/` — Group Lasso Model Implementation and Runtime Optimization
- `/case-studies/oracle-trino/` — Oracle-to-Trino Pipeline Modernization
- `/robots.txt` — Crawler policy and sitemap location
- `/sitemap.xml` — Public route index

The site deliberately has no resume download.

## Deploying to Vercel

1. Import this repository into Vercel and use its framework auto-detection.
2. In the Vercel project settings, expose Vercel system environment variables to the application.
3. Set a strong `DJANGO_SECRET_KEY` for both Production and Preview.
4. If a custom domain is added later, optionally set `SITE_URL` to its full origin, such as `https://example.com`.
5. If custom domains need an explicit Django allowlist, optionally set `DJANGO_ALLOWED_HOSTS` to the exact comma-separated hostnames.
6. Deploy without adding a build command or output-directory override. Vercel detects the root `manage.py` and Django WSGI application.
7. After deployment, verify the public routes, static CSS/JavaScript/fonts/images, response security headers, canonical and social metadata, the social preview image, `robots.txt`, `sitemap.xml`, and branded 404/500 pages.

Vercel's deployed filesystem is read-only except for ephemeral files under `/tmp`. The current site does not need persistent runtime state; any future database, uploads, sessions, or generated persistent files would require an external managed store.
