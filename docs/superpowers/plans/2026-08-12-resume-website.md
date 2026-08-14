# Resume Website Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a responsive, local-first Django portfolio that positions Norman Hoang as a banking-focused Quantitative Developer and presents verified experience through three confidentiality-safe case studies.

**Architecture:** A single Django project (`portfolio`) contains one presentation app (`website`). Source-controlled Python dictionaries in `website/content.py` are the only content source; thin views pass those structures to reusable server-rendered templates. Custom static CSS and minimal vanilla JavaScript provide the approved editorial-technical visual system without a database, CMS, or frontend build step.

**Tech Stack:** Python 3.12, Django 5.2 LTS, Django templates, custom CSS, vanilla JavaScript, Django `SimpleTestCase`, locally bundled font/image assets

**Spec:** `docs/superpowers/specs/2026-08-12-resume-website-design.md`

## Global Constraints

- Use Python 3.12 and `Django>=5.2,<5.3`.
- Keep the site server-rendered with no custom models, CMS, accounts, admin editing, forms, analytics, cookies, or frontend build tools.
- Treat `01-candidate-profile.md` as canonical when it conflicts with `Profile.pdf`.
- Publish only employer names, technologies, responsibilities, and approved résumé metrics; abstract proprietary banking implementation details.
- Omit the résumé action, headshot, phone, compensation, work authorization, languages, organization logos, and “Open to work” messaging.
- Use the approved palette and locally bundled STIX Two Text, IBM Plex Sans, and IBM Plex Mono.
- Support keyboard use, visible focus, semantic landmarks, reduced motion, and 320 CSS pixels without horizontal overflow.
- Do not add deployment, production database, blog, search, account, localization, dark-theme, or contact-form scope.

---

### Task 1: Django foundation and public route contract

**Files:**
- Create: `.python-version`
- Create: `requirements.txt`
- Create: `manage.py`
- Create: `portfolio/__init__.py`
- Create: `portfolio/settings.py`
- Create: `portfolio/urls.py`
- Create: `portfolio/asgi.py`
- Create: `portfolio/wsgi.py`
- Create: `website/__init__.py`
- Create: `website/apps.py`
- Create: `website/urls.py`
- Create: `website/views.py`
- Create: `website/tests/__init__.py`
- Create: `website/tests/test_routes.py`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: Python 3.12 and Django 5.2 LTS.
- Produces: named routes `website:home`, `website:experience`, `website:case_studies`, and `website:case_study_detail`; view callables `home`, `experience`, `case_studies`, and `case_study_detail(request, slug)`.

- [ ] **Step 1: Record the local runtime and dependency**

```text
# .python-version
3.12

# requirements.txt
Django>=5.2,<5.3
```

Create the virtual environment and install the dependency:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

- [ ] **Step 2: Write the failing route tests**

```python
# website/tests/test_routes.py
from django.test import SimpleTestCase
from django.urls import reverse


class PublicRouteTests(SimpleTestCase):
    def test_primary_pages_render(self):
        for route_name in (
            "website:home",
            "website:experience",
            "website:case_studies",
        ):
            with self.subTest(route_name=route_name):
                self.assertEqual(self.client.get(reverse(route_name)).status_code, 200)

    def test_each_case_study_route_renders(self):
        for slug in ("risk-calibration", "group-lasso", "oracle-trino"):
            with self.subTest(slug=slug):
                response = self.client.get(
                    reverse("website:case_study_detail", kwargs={"slug": slug})
                )
                self.assertEqual(response.status_code, 200)

    def test_unknown_case_study_returns_404(self):
        response = self.client.get(
            reverse("website:case_study_detail", kwargs={"slug": "unknown"})
        )
        self.assertEqual(response.status_code, 404)
```

- [ ] **Step 3: Run the route tests and verify RED**

Run:

```bash
.venv/bin/python manage.py test website.tests.test_routes -v 2
```

Expected: FAIL because `manage.py`, the Django project, or the named routes do not exist yet.

- [ ] **Step 4: Add the minimal Django project and route implementations**

Use standard `manage.py`, ASGI, and WSGI entry points targeting `portfolio.settings`. Configure `portfolio/settings.py` with:

```python
INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "website",
]
ROOT_URLCONF = "portfolio.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
    ]},
}]
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

Set a clearly local-only `SECRET_KEY`, `DEBUG = True`, and `ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]`. Do not configure a database because the site has no database-backed behavior.

Route the project root to `website.urls`. Define:

```python
# website/urls.py
from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    path("", views.home, name="home"),
    path("experience/", views.experience, name="experience"),
    path("case-studies/", views.case_studies, name="case_studies"),
    path("case-studies/<slug:slug>/", views.case_study_detail, name="case_study_detail"),
]
```

Use temporary `HttpResponse` bodies for the three page views. In `case_study_detail`, return a response only for the three approved slugs and raise `Http404` otherwise. Task 3 replaces these temporary bodies with templates.

- [ ] **Step 5: Protect local source materials from accidental commits**

Append these exact entries to `.gitignore` while keeping the files available locally:

```gitignore
# Private source materials
01-candidate-profile.md
02-behavioral-profile.md
03-writing-style.md
04-job-evaluation.md
05-cv-templates.md
07-interview-prep.md
Profile.pdf
Norman_Hoang_Resume_BofA_VP_CrossAssetQuant_v1_2page.docx
```

- [ ] **Step 6: Run tests and project checks to verify GREEN**

Run:

```bash
.venv/bin/python manage.py test website.tests.test_routes -v 2
.venv/bin/python manage.py check
```

Expected: 3 route tests pass and Django reports no issues.

- [ ] **Step 7: Commit**

```bash
git add .gitignore .python-version requirements.txt manage.py portfolio website
git commit -m "feat: scaffold Django portfolio"
```

---

### Task 2: Verified content source and case-study lookup

**Files:**
- Create: `website/content.py`
- Create: `website/tests/test_content.py`
- Modify: `website/views.py`

**Interfaces:**
- Consumes: route names and view signatures from Task 1.
- Produces: `SITE`, `PROOF_POINTS`, `SKILL_GROUPS`, `EXPERIENCE`, `EDUCATION`, `ACADEMIC_PROJECTS`, `CREDENTIALS`, `INDEPENDENT_WORK`, ordered `CASE_STUDIES`, `CASE_STUDIES_BY_SLUG`, and `get_case_study(slug: str) -> dict | None`.

- [ ] **Step 1: Write failing content-contract tests**

```python
# website/tests/test_content.py
from django.test import SimpleTestCase

from website.content import CASE_STUDIES, SITE, get_case_study


class ContentContractTests(SimpleTestCase):
    def test_site_identity_and_contact_are_canonical(self):
        self.assertEqual(SITE["name"], "Norman Hoang")
        self.assertEqual(SITE["location"], "New York, NY")
        self.assertEqual(SITE["email"], "normanhoang@gmail.com")
        self.assertEqual(SITE["linkedin"], "https://www.linkedin.com/in/normanhoang/")
        self.assertEqual(SITE["github"], "https://github.com/normanhoang/")

    def test_case_studies_have_unique_approved_slugs_and_sections(self):
        self.assertEqual(
            [study["slug"] for study in CASE_STUDIES],
            ["risk-calibration", "group-lasso", "oracle-trino"],
        )
        for study in CASE_STUDIES:
            with self.subTest(slug=study["slug"]):
                self.assertEqual(
                    list(study["sections"]),
                    ["Context", "Problem", "Constraints", "Approach", "Measurable impact"],
                )
                self.assertTrue(study["technologies"])

    def test_lookup_returns_none_for_unknown_slug(self):
        self.assertIsNone(get_case_study("unknown"))

    def test_pipeline_claims_preserve_scope_and_metrics(self):
        study = get_case_study("oracle-trino")
        combined = " ".join(study["sections"].values())
        self.assertIn("co-designed", combined)
        self.assertIn("led the implementation", combined)
        self.assertIn("8 hours", combined)
        self.assertIn("2 hours", combined)

    def test_group_lasso_claims_preserve_metrics(self):
        study = get_case_study("group-lasso")
        combined = " ".join(study["sections"].values())
        self.assertIn("70%", combined)
        self.assertIn("60%", combined)
        self.assertIn("one-billion-row", combined)
```

- [ ] **Step 2: Run the content tests and verify RED**

Run:

```bash
.venv/bin/python manage.py test website.tests.test_content -v 2
```

Expected: ERROR because `website.content` does not exist.

- [ ] **Step 3: Implement the single content source**

Create ordinary immutable-at-runtime tuples/dictionaries; do not add models or a generic content framework. Define `SITE` with the exact identity/contact values in the test plus the approved headline, supporting line, current-employer line, and repository URLs.

Define the three case studies with these exact titles, labels, and evidence:

```python
CASE_STUDIES = (
    {
        "slug": "risk-calibration",
        "title": "Financial Risk Calibration Library",
        "eyebrow": "Risk & regulatory analytics",
        "summary": "Improving reusable calibration tooling whose outputs support IFRS, CECL, and CCAR risk processes.",
        "sections": {
            "Context": "Within Bank of America Global Risk Analytics, I contribute to an in-house financial risk calibration library used across regulated risk processes.",
            "Problem": "The library calibrates Default Rate Transition, Loss Given Default, Balance, NPA, TTR, and macrofactor moments. Those outputs need to remain consistent and reusable as they feed IFRS, CECL, and CCAR workflows.",
            "Constraints": "The work sits inside a shared banking platform with model-governance expectations and confidential data and implementation details. This public account therefore focuses on responsibilities and process, not internal parameters or controls.",
            "Approach": "I develop improvements to shared calibration routines and their reusable interfaces, with an emphasis on numerical consistency, verification, and maintainability for model-development and execution workflows.",
            "Measurable impact": "The resulting calibration outputs support three major accounting and stress-testing frameworks: IFRS, CECL, and CCAR.",
        },
        "technologies": ("Python", "Numerical methods", "Statistical modeling", "Risk calibration"),
    },
    {
        "slug": "group-lasso",
        "title": "Group Lasso Model Implementation",
        "eyebrow": "Model implementation & optimization",
        "summary": "Research-to-production implementation of grouped regression methods with measured runtime improvements.",
        "sections": {
            "Context": "As an Assistant Vice President in Global Risk Analytics, I implemented quantitative regression tooling for consumer-credit, auto-loan, and mortgage modeling workflows.",
            "Problem": "The team needed Group Lasso support for logistic and linear regression, together with faster execution for custom algorithms operating on large credit datasets.",
            "Constraints": "The implementation had to translate multiple research papers into reliable Python while preserving model behavior across credit-card and mortgage benchmarks and distributed prediction workloads.",
            "Approach": "I programmed a Blockwise Coordinate Gradient Descent Group Lasso module from scratch, used vectorized NumPy algorithms for parallel SIMD calculations, and applied a MapReduce implementation of Nesterov Momentum to PySpark prediction models.",
            "Measurable impact": "Vectorization reduced total regression runtime by 70%. The MapReduce optimization reduced custom-regression runtime by 60% on a one-billion-row dataset.",
        },
        "technologies": ("Python", "NumPy", "PySpark", "MapReduce", "Group Lasso"),
    },
    {
        "slug": "oracle-trino",
        "title": "Oracle-to-Trino Pipeline Modernization",
        "eyebrow": "Production-scale data engineering",
        "summary": "Rebuilding an unreliable bulk extraction into a parallel, skew-aware pipeline for downstream analytics.",
        "sections": {
            "Context": "A recurring Oracle bulk-data pull supported downstream quantitative and analytics work but had become an operational bottleneck.",
            "Problem": "The extraction ran for more than 8 hours and failed repeatedly, making the delivery window unreliable.",
            "Constraints": "The source data was skewed across systems and time periods, and the output still needed to land in the existing Hadoop and Hive environment.",
            "Approach": "I co-designed the solution with the team, led the implementation, and wrote the code for a parallel Trino extraction chunked by source system and time period to control skew.",
            "Measurable impact": "The rebuilt pipeline cut runtime from more than 8 hours to 2 hours and eliminated the recurring failures.",
        },
        "technologies": ("Python", "SQL", "Oracle", "Trino", "Hadoop", "Hive"),
    },
)
CASE_STUDIES_BY_SLUG = {study["slug"]: study for study in CASE_STUDIES}


def get_case_study(slug: str):
    return CASE_STUDIES_BY_SLUG.get(slug)
```

Also encode the approved proof points, capability groups, professional roles and canonical dates, education/coursework, four academic projects, four credentials, FinApp/CloudKit/working-paper entries, and Beyond work line from the spec and `01-candidate-profile.md`. Keep all public copy confidentiality-safe and omit every prohibited field listed in Global Constraints.

- [ ] **Step 4: Replace the temporary detail lookup**

In `website/views.py`, use `get_case_study(slug)` and raise `Http404("Case study not found")` when it returns `None`. Keep temporary `HttpResponse` rendering until Task 3.

- [ ] **Step 5: Run content and route tests to verify GREEN**

Run:

```bash
.venv/bin/python manage.py test website.tests.test_content website.tests.test_routes -v 2
```

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add website/content.py website/views.py website/tests/test_content.py
git commit -m "feat: add verified portfolio content"
```

---

### Task 3: Server-rendered page templates and confidentiality checks

**Files:**
- Create: `website/templates/website/base.html`
- Create: `website/templates/website/includes/case_card.html`
- Create: `website/templates/website/includes/contact.html`
- Create: `website/templates/website/home.html`
- Create: `website/templates/website/experience.html`
- Create: `website/templates/website/case_studies.html`
- Create: `website/templates/website/case_study_detail.html`
- Create: `website/tests/test_pages.py`
- Modify: `website/views.py`

**Interfaces:**
- Consumes: all content constants and `get_case_study()` from Task 2.
- Produces: semantic HTML pages with stable landmarks and the approved navigation/content hierarchy.

- [ ] **Step 1: Write failing rendered-page tests**

```python
# website/tests/test_pages.py
from django.test import SimpleTestCase
from django.urls import reverse


class RenderedPageTests(SimpleTestCase):
    def test_home_renders_positioning_proof_and_contact(self):
        response = self.client.get(reverse("website:home"))
        self.assertContains(response, "I build quantitative risk and pricing systems for banking.")
        self.assertContains(response, "Vice President in Global Risk Analytics at Bank of America")
        self.assertContains(response, "~2B")
        self.assertContains(response, "IFRS · CECL · CCAR")
        self.assertContains(response, "normanhoang@gmail.com")
        self.assertContains(response, "New York, NY")

    def test_experience_renders_official_titles_and_canonical_dates(self):
        response = self.client.get(reverse("website:experience"))
        self.assertContains(response, "Vice President, Quantitative Finance Analyst")
        self.assertContains(response, "Jan 2023—Present")
        self.assertContains(response, "Assistant Vice President, Quantitative Finance Analyst")
        self.assertContains(response, "Aug 2019—Dec 2022")
        self.assertContains(response, "M.S. in Quantitative Finance")
        self.assertContains(response, "C++ Programming")

    def test_case_study_index_links_to_all_detail_pages(self):
        response = self.client.get(reverse("website:case_studies"))
        for slug in ("risk-calibration", "group-lasso", "oracle-trino"):
            self.assertContains(
                response,
                reverse("website:case_study_detail", kwargs={"slug": slug}),
            )

    def test_case_detail_uses_shared_section_structure(self):
        response = self.client.get(
            reverse("website:case_study_detail", kwargs={"slug": "group-lasso"})
        )
        for heading in ("Context", "Problem", "Constraints", "Approach", "Measurable impact", "Technologies"):
            self.assertContains(response, heading)

    def test_public_pages_omit_prohibited_personal_and_job_search_content(self):
        for route_name in ("website:home", "website:experience", "website:case_studies"):
            response = self.client.get(reverse(route_name))
            body = response.content.decode()
            with self.subTest(route_name=route_name):
                self.assertNotRegex(body, r'href=["\']tel:')
                self.assertNotRegex(body.lower(), r"\b(?:salary|compensation)\b")
                self.assertNotIn("work authorization", body.lower())
                self.assertNotIn("download résumé", body.lower())

    def test_external_links_are_safe(self):
        response = self.client.get(reverse("website:home"))
        self.assertContains(response, 'target="_blank"')
        self.assertContains(response, 'rel="noreferrer noopener"')
```

- [ ] **Step 2: Run the page tests and verify RED**

Run:

```bash
.venv/bin/python manage.py test website.tests.test_pages -v 2
```

Expected: FAIL because the temporary responses do not contain the approved page content.

- [ ] **Step 3: Implement thin context views**

Render templates with only the context they consume:

```python
def home(request):
    return render(request, "website/home.html", {
        "site": SITE,
        "proof_points": PROOF_POINTS,
        "skill_groups": SKILL_GROUPS,
        "case_studies": CASE_STUDIES,
        "independent_work": INDEPENDENT_WORK,
    })


def experience(request):
    return render(request, "website/experience.html", {
        "site": SITE,
        "experience": EXPERIENCE,
        "education": EDUCATION,
        "academic_projects": ACADEMIC_PROJECTS,
        "credentials": CREDENTIALS,
    })


def case_studies(request):
    return render(request, "website/case_studies.html", {
        "site": SITE,
        "case_studies": CASE_STUDIES,
    })


def case_study_detail(request, slug):
    study = get_case_study(slug)
    if study is None:
        raise Http404("Case study not found")
    return render(request, "website/case_study_detail.html", {
        "site": SITE,
        "study": study,
    })
```

- [ ] **Step 4: Implement the shared document shell**

`base.html` must load `{% static 'website/css/site.css' %}` and defer `{% static 'website/js/site.js' %}`. Add a skip link, `<header>`, labeled `<nav>`, `<main id="main-content">`, and `<footer>`. Use `request.resolver_match.url_name` for `aria-current="page"`. Contact links point to `{% url 'website:home' %}#contact` from every page.

Header skeleton:

```html
<a class="skip-link" href="#main-content">Skip to content</a>
<header class="site-header">
  <a class="wordmark" href="{% url 'website:home' %}">Norman Hoang</a>
  <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="primary-navigation">
    <span>Menu</span>
  </button>
  <nav id="primary-navigation" class="primary-nav" aria-label="Primary navigation">
    <!-- Home, Experience, Case Studies, Contact -->
  </nav>
</header>
```

- [ ] **Step 5: Implement the four page templates**

Use semantic sections and content-driven loops. Required structural choices:

- `home.html`: hero with one `h1`, two actions, proof ledger, three case cards, three capability groups, Independent Work with a FinApp media figure that Task 4 fills with the bundled image, Beyond work, and contact include.
- `experience.html`: page header, reverse-chronological `<ol>` timeline, education, coursework, four academic project cards, credentials, and contact include.
- `case_studies.html`: confidentiality note followed by three case cards and contact include.
- `case_study_detail.html`: title/summary header, ordered section loop, technologies list, links to Case Studies and Contact.

Render shared case cards through:

```html
{% include "website/includes/case_card.html" with study=study %}
```

Render the detail sections through:

```html
{% for heading, copy in study.sections.items %}
  <section class="case-section" aria-labelledby="section-{{ forloop.counter }}">
    <p class="section-index" aria-hidden="true">0{{ forloop.counter }}</p>
    <div>
      <h2 id="section-{{ forloop.counter }}">{{ heading }}</h2>
      <p>{{ copy }}</p>
    </div>
  </section>
{% endfor %}
```

Every external link uses `target="_blank" rel="noreferrer noopener"` and includes visually hidden “opens in a new tab” text. Do not render any résumé control.

- [ ] **Step 6: Run the full Django test suite to verify GREEN**

Run:

```bash
.venv/bin/python manage.py test -v 2
```

Expected: route, content, and rendered-page tests all pass.

- [ ] **Step 7: Commit**

```bash
git add website/views.py website/templates website/tests/test_pages.py
git commit -m "feat: render portfolio pages"
```

---

### Task 4: Editorial-technical design system and accessible interaction

**Files:**
- Create: `website/static/website/css/site.css`
- Create: `website/static/website/js/site.js`
- Create: `website/static/website/fonts/STIXTwoText-Variable.ttf`
- Create: `website/static/website/fonts/IBMPlexSans-Variable.ttf`
- Create: `website/static/website/fonts/IBMPlexMono-Variable.ttf`
- Create: `website/static/website/fonts/OFL-STIXTwoText.txt`
- Create: `website/static/website/fonts/OFL-IBMPlex.txt`
- Create: `website/static/website/img/finapp-dashboard-light.png`
- Create: `website/tests/test_static_assets.py`
- Modify: `website/templates/website/home.html`
- Modify: `website/templates/website/base.html`
- Modify: `website/templates/website/case_study_detail.html`

**Interfaces:**
- Consumes: stable semantic markup and class names from Task 3.
- Produces: the approved visual system, risk-surface signature, authentic FinApp image, responsive mobile navigation, and locally resolved static assets.

- [ ] **Step 1: Write failing static/accessibility contract tests**

```python
# website/tests/test_static_assets.py
from django.contrib.staticfiles import finders
from django.test import SimpleTestCase
from django.urls import reverse


class StaticAssetTests(SimpleTestCase):
    def test_required_static_assets_are_discoverable(self):
        for path in (
            "website/css/site.css",
            "website/js/site.js",
            "website/fonts/STIXTwoText-Variable.ttf",
            "website/fonts/IBMPlexSans-Variable.ttf",
            "website/fonts/IBMPlexMono-Variable.ttf",
            "website/img/finapp-dashboard-light.png",
        ):
            with self.subTest(path=path):
                self.assertIsNotNone(finders.find(path))

    def test_home_has_accessible_navigation_and_decorative_graphics(self):
        response = self.client.get(reverse("website:home"))
        self.assertContains(response, 'aria-controls="primary-navigation"')
        self.assertContains(response, 'aria-expanded="false"')
        self.assertContains(response, 'class="risk-surface"')
        self.assertContains(response, 'aria-hidden="true"')
        self.assertContains(response, "FinApp dashboard showing account balances")

    def test_site_does_not_request_remote_fonts_or_tracking(self):
        response = self.client.get(reverse("website:home"))
        body = response.content.decode()
        self.assertNotIn("fonts.googleapis.com", body)
        self.assertNotIn("fonts.gstatic.com", body)
        self.assertNotIn("googletagmanager", body)
```

- [ ] **Step 2: Run the asset tests and verify RED**

Run:

```bash
.venv/bin/python manage.py test website.tests.test_static_assets -v 2
```

Expected: FAIL because the static assets and risk-surface markup do not exist.

- [ ] **Step 3: Bundle approved public assets and licenses**

Download the three font files and their licenses from the upstream Google Fonts repository, and download the authentic FinApp image from Norman’s public repository. Do not hotlink any runtime asset. Use these sources:

```text
https://github.com/google/fonts/tree/main/ofl/stixtwotext
https://github.com/google/fonts/tree/main/ofl/ibmplexsans
https://github.com/google/fonts/tree/main/ofl/ibmplexmono
https://raw.githubusercontent.com/normanhoang/fin_app/main/AppStore/screenshots/00-dashboard-light.png
```

Verify each downloaded file is nonempty and the image is a valid PNG before continuing.

- [ ] **Step 4: Add the risk-surface signature and real FinApp image**

Add an inline decorative SVG to the hero and detail header with `class="risk-surface" aria-hidden="true" focusable="false"`. Use 4–6 smooth contour paths, one cobalt path, one copper point annotation, and no text embedded in the SVG.

Render the FinApp image with Django staticfiles:

```html
<img
  src="{% static 'website/img/finapp-dashboard-light.png' %}"
  alt="FinApp dashboard showing account balances, spending, budgets, and upcoming bills"
  width="1290"
  height="2796"
  loading="lazy"
>
```

- [ ] **Step 5: Implement the approved CSS system**

At the top of `site.css`, define local variable fonts and exact design tokens:

```css
@font-face { font-family: "STIX Two Text"; src: url("../fonts/STIXTwoText-Variable.ttf") format("truetype"); font-weight: 400 700; font-display: swap; }
@font-face { font-family: "IBM Plex Sans"; src: url("../fonts/IBMPlexSans-Variable.ttf") format("truetype"); font-weight: 300 700; font-display: swap; }
@font-face { font-family: "IBM Plex Mono"; src: url("../fonts/IBMPlexMono-Variable.ttf") format("truetype"); font-weight: 400 700; font-display: swap; }

:root {
  --ledger: #f5f7fa;
  --paper: #ffffff;
  --ink: #14213d;
  --cobalt: #2457c5;
  --copper: #b5683a;
  --rule: #d5dce5;
  --slate: #5c6675;
  --display: "STIX Two Text", Georgia, serif;
  --body: "IBM Plex Sans", Arial, sans-serif;
  --mono: "IBM Plex Mono", monospace;
  --content: min(1180px, calc(100vw - 2rem));
}
```

Implement:

- zero horizontal overflow and `box-sizing: border-box`
- a sticky translucent header with fine bottom rule
- skip-link and `:focus-visible` states
- responsive hero: asymmetric two-column desktop, single-column mobile
- proof ledger with tabular mono labels and no vanity-stat card styling
- case-card, timeline, capability, academic-project, credential, contact, and footer layouts
- code-native contour animation using stroke dash offset
- mobile navigation below 760px
- layout adjustments at 1024px, 760px, and 480px
- a `@media (prefers-reduced-motion: reduce)` block that disables animation and smooth scrolling
- a `@media (prefers-contrast: more)` block that strengthens rules and focus outlines

Do not add gradients, excessive rounded cards, drop-shadow stacks, parallax, or generic numbered decoration unrelated to sequence. Case-study section numbers are permitted because they encode the approved reading sequence.

- [ ] **Step 6: Implement minimal mobile-menu behavior**

```javascript
const toggle = document.querySelector(".nav-toggle");
const navigation = document.querySelector("#primary-navigation");

if (toggle && navigation) {
  const closeMenu = () => {
    toggle.setAttribute("aria-expanded", "false");
    document.documentElement.classList.remove("nav-open");
  };

  toggle.addEventListener("click", () => {
    const isOpen = toggle.getAttribute("aria-expanded") === "true";
    toggle.setAttribute("aria-expanded", String(!isOpen));
    document.documentElement.classList.toggle("nav-open", !isOpen);
  });

  navigation.addEventListener("click", (event) => {
    if (event.target.closest("a")) closeMenu();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeMenu();
      toggle.focus();
    }
  });
}
```

- [ ] **Step 7: Run the full suite and static collection check**

Run:

```bash
.venv/bin/python manage.py test -v 2
.venv/bin/python manage.py collectstatic --noinput --dry-run
```

Expected: all tests pass and every static asset is discovered without collisions.

- [ ] **Step 8: Commit**

```bash
git add website/static website/templates/website website/tests/test_static_assets.py
git commit -m "feat: add responsive visual system"
```

---

### Task 5: Local documentation and acceptance verification

**Files:**
- Create: `README.md`
- Create: `docs/verification/responsive-review.md`

**Interfaces:**
- Consumes: the complete Django application and static assets from Tasks 1–4.
- Produces: reproducible local setup instructions and a recorded desktop/mobile acceptance review.

- [ ] **Step 1: Write concise local setup documentation**

`README.md` must include exactly these setup commands:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py runserver
```

Also document `python manage.py test` and `python manage.py check`, the local URL `http://127.0.0.1:8000/`, the public route list, and the deliberate absence of a résumé download and deployment configuration.

- [ ] **Step 2: Run fresh automated verification**

Run:

```bash
.venv/bin/python --version
.venv/bin/python -m django --version
.venv/bin/python manage.py check
.venv/bin/python manage.py test -v 2
.venv/bin/python manage.py collectstatic --noinput --dry-run
git diff --check
```

Expected: Python reports 3.12.x, Django reports 5.2.x, checks and tests exit zero, static discovery succeeds, and the diff has no whitespace errors.

- [ ] **Step 3: Capture representative browser screenshots**

Start the local server on `127.0.0.1:8000`. Use installed Google Chrome in headless mode to capture Home at 1440×1200, 768×1024, 375×900, and 320×900, plus Experience and one case-study page at 375×900. Save temporary captures outside the repository under `/tmp/resume-website-verification/`.

Inspect every image for clipping, horizontal overflow, unreadable type, obscured navigation, missing assets, and broken hierarchy. Exercise the menu at mobile width and verify Escape closes it and returns focus. Verify reduced motion by emulating `prefers-reduced-motion: reduce` and confirming contour motion is disabled.

- [ ] **Step 4: Record the acceptance evidence**

Write `docs/verification/responsive-review.md` with:

```markdown
# Responsive Review

- Date: 2026-08-12
- Routes reviewed: Home, Experience, Case Studies, Group Lasso detail
- Widths reviewed: 320, 375, 768, 1440 CSS pixels
- Horizontal overflow: none
- Mobile navigation: opens, closes by link selection, closes with Escape, restores focus
- Reduced motion: contour animation disabled
- Browser console: no errors
- Content check: approved titles, dates, metrics, links, and omissions confirmed
```

If any line is false, fix the defect using a new failing test where feasible, rerun the affected verification, and record only the observed result.

- [ ] **Step 5: Commit**

```bash
git add README.md docs/verification/responsive-review.md
git commit -m "docs: add local setup and verification"
```

- [ ] **Step 6: Run the final verification gate**

Run:

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py test -v 2
.venv/bin/python manage.py collectstatic --noinput --dry-run
git status --short
```

Expected: checks and tests pass; static assets resolve; only intentionally ignored local source materials and generated verification artifacts remain outside Git status.
