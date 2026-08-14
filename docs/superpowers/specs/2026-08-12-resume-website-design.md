# Norman Hoang Resume Website Design

## Purpose

Build a server-rendered Django portfolio that positions Norman Hoang for Quantitative Developer roles in banking. The site must establish credibility quickly for hiring managers, then support deeper review of banking experience and selected technical case studies.

The positioning hierarchy is:

1. Risk and pricing technology
2. Quantitative model implementation
3. Regulatory analytics
4. Production-scale data engineering

The site targets experienced individual-contributor roles across the mid-level and senior bands. The hero uses “Quantitative Developer” as professional positioning, while the Experience page preserves official employer titles.

## Audience and Primary Journey

The primary audience is a hiring manager or recruiter at a bank. The intended journey is:

1. Read the banking-specific thesis.
2. Scan three evidence-backed proof points.
3. Open the flagship case studies.
4. Review the full experience and supporting skills.
5. Contact Norman by email or LinkedIn.

The homepage thesis is:

> I build quantitative risk and pricing systems for banking.

Supporting line:

> Quantitative Developer specializing in model implementation, regulatory analytics, and production-scale data engineering.

The homepage also states that Norman is currently a Vice President in Global Risk Analytics at Bank of America.

## Architecture

Use Django 5.2 LTS with Python 3.12. The site is one Django project with one `website` application. It uses ordinary Django views and templates, custom CSS, and minimal vanilla JavaScript.

There are no custom database models, CMS, accounts, admin editing, forms, analytics, cookies, or frontend build tools. Site content lives in a source-controlled Python content module and is rendered into reusable templates. A shared case-study schema drives the index cards and individual detail pages without duplicating content.

The site must run locally after installing `requirements.txt` and executing `python manage.py runserver`. Production-readiness requirements for Vercel are defined by the [Vercel Launch Readiness Design](2026-08-14-vercel-launch-readiness-design.md), which extends this specification.

## Information Architecture

### Global navigation

- Home
- Experience
- Case Studies
- Contact, linking to the dedicated `/contact/` page

The header wordmark is “Norman Hoang.” The mobile header uses an accessible menu button with correct expanded state and keyboard behavior.

### Home

- Banking-specific hero thesis
- Primary action: “View case studies”
- Secondary action: Experience
- Proof ledger above the fold:
  - `~2B` market-data records processed daily
  - `58 → 119` users of the shared statistical library
  - `IFRS · CECL · CCAR` risk processes supported by calibration outputs
- Selected case-study previews
- Evidence-linked capability groups
- Independent Work:
  - FinApp, with one authentic light-mode screenshot and a direct repository link
  - Mathematics of Model Explainability, listed as an internal, non-peer-reviewed working paper for Model Risk Management covering XGBoost, SHAP, and feature importance, without a public document link

### Experience

- Reverse-chronological professional timeline
- Detailed Bank of America Vice President and Assistant Vice President entries
- Official titles and approved canonical dates:
  - Vice President, Quantitative Finance Analyst: January 2023–present
  - Assistant Vice President, Quantitative Finance Analyst: August 2019–December 2022
- Condensed Extron Electronics and Edwards Lifesciences experience
- Education:
  - M.S. in Quantitative Finance, Fordham University
  - B.S. in Electrical Engineering, Specialization in Systems and Signals, University of California, Irvine
- Selected M.S. coursework: stochastic calculus, derivatives and fixed income, risk management, advanced C++, and computational finance
- Four compact academic-project entries:
  - Algorithmic trading prototype
  - C++ pricing and risk library
  - Volatility-arbitrage strategy, linked to its public repository
  - S&P 1500 forecasting model, linked to its public repository
- Selected credentials:
  - C++ Programming — Baruch College
  - Statistical Thinking for Data Science and Analytics — Columbia University
  - Professional Program Certificate in Data Science — Microsoft
  - GitHub Foundations — GitHub
- Leadership & community:
  - Led the Global Risk Analytics Knowledge Share program for three years
  - Served as a member of the Jersey City Site Team
  - Founded and led the employee book club

### Case Studies index

Introduce the confidentiality boundary and link to four flagship case studies:

1. Financial Risk Calibration Library
2. Spark and Python Quant Platform Modernization
3. Group Lasso Model Implementation and Runtime Optimization
4. Oracle-to-Trino Pipeline Modernization

### Case-study detail pages

Every case study uses the same structure:

1. Context
2. Problem
3. Constraints
4. Approach
5. Measurable impact
6. Technologies

The risk-calibration study describes ongoing contributions and does not imply sole ownership. The pipeline study states that the solution was co-designed with the team and that Norman led implementation and wrote the code. The Group Lasso study may state that Norman programmed the module from scratch based on research papers.

No confidential source code, internal datasets, model parameters, control details, architecture diagrams, or invented metrics may appear.

## Content Rules

- Use concise first person in the introduction and case-study commentary.
- Use factual résumé-style language for experience entries.
- Employer names, technologies, responsibilities, and approved résumé metrics may be public.
- Abstract proprietary banking implementation details.
- Treat `01-candidate-profile.md` as canonical when it conflicts with the older LinkedIn PDF.
- Preserve official employment titles on the Experience page.
- Describe the model-explainability item as an internal working paper for Model Risk Management covering XGBoost, SHAP, and feature importance; explicitly state that it is not peer-reviewed.
- Disclose Claude Code assistance in the FinApp detail while emphasizing architecture, security controls, tests, and Norman’s engineering decisions.
- Link the public FinApp, volatility-arbitrage, and S&P 1500 repositories.

The site omits:

- Résumé download until a public-safe PDF is supplied
- Headshot
- Phone number
- Compensation expectations
- Work-authorization details
- Languages
- Employer, university, certification, and technology logos
- “Open to work” messaging
- Testimonials or unsupported claims

## Contact and External Links

- Location: New York, NY
- Email: `normanhoang@gmail.com`
- LinkedIn: `https://www.linkedin.com/in/normanhoang/`
- GitHub: `https://github.com/normanhoang/`
- FinApp: `https://github.com/normanhoang/fin_app`
- Volatility arbitrage: `https://github.com/normanhoang/cpp_final_project`
- S&P 1500 forecasting: `https://github.com/normanhoang/SVM_Analysis`

Email and LinkedIn are the primary contact methods. External links open safely and identify that they leave the site. There is no contact form.

## Visual System

The direction is a light, editorial-technical “risk-desk dossier.” It should feel precise and banking-specific without resembling a neon trading terminal, a generic corporate résumé, or a newspaper template.

### Palette

- Ledger white: `#F5F7FA`
- Ink navy: `#14213D`
- Signal cobalt: `#2457C5`
- Calibration copper: `#B5683A`
- Rule gray: `#D5DCE5`
- Secondary slate: `#5C6675`

Cobalt carries links and actions. Copper is reserved for risk and model annotations.

### Typography

- STIX Two Text for restrained editorial headlines
- IBM Plex Sans for body copy and navigation
- IBM Plex Mono for dates, metrics, model names, and data labels

Font files are bundled locally; the rendered site makes no third-party font requests.

### Layout and signature

Use generous but disciplined spacing, strong typographic hierarchy, fine rules, structured side labels, and proof-led layouts. The signature element is a subtle risk-surface contour treatment in the hero and case-study headers. It is supporting information texture, not decoration that competes with the copy.

The hero contains one restrained resolving contour animation. Hover and focus transitions are subtle. There is no parallax, scroll hijacking, or repeated scroll-reveal system.

Organization names remain text-only. The banking case studies use abstract, code-native diagrams or annotations rather than fabricated screenshots. FinApp uses one authentic bundled light-mode dashboard screenshot from its public repository.

## Responsive and Accessibility Requirements

- Layout works without horizontal scrolling from 320 CSS pixels upward.
- Desktop, tablet, and mobile layouts preserve content hierarchy.
- Navigation, links, and controls are keyboard operable.
- Visible focus states meet or exceed the contrast of surrounding controls.
- Text and interactive elements meet WCAG 2.2 AA color contrast.
- Semantic landmarks and heading order are valid.
- The mobile-menu button exposes its label and expanded state.
- Decorative contour graphics are hidden from assistive technology.
- Meaning is never conveyed by color alone.
- `prefers-reduced-motion: reduce` disables nonessential motion.
- FinApp imagery has useful alternative text and responsive dimensions.

## Error Handling

- An unknown case-study slug returns Django’s 404 response.
- Unknown routes render a branded 404 page with the shared navigation and a route home.
- Server errors render a branded 500 page without exception details or internal state.
- Navigation never exposes an inactive résumé action.
- Templates should not contain optional empty sections.
- External-link failures remain ordinary browser behavior; the site does not proxy or validate third-party services at runtime.

## Verification

Automated Django tests must verify:

- Home, Experience, Case Studies, Contact, and all four case-study URLs return HTTP 200.
- Unknown case-study slugs return HTTP 404.
- Canonical positioning, proof points, contact details, official titles, and approved dates render on the correct pages.
- The case-study index links to every detail page.
- The résumé action, phone number, compensation, and work-authorization details do not render.
- Static asset references resolve through Django’s staticfiles system.
- Canonical and social metadata use absolute production URLs.
- `robots.txt`, `sitemap.xml`, branded error responses, Vercel settings, and response-header configuration match the launch-readiness extension.

Manual verification must cover:

- Fresh local installation and `manage.py check`
- Full Django test suite
- Desktop and mobile screenshots at representative widths
- Mobile navigation interaction
- Keyboard focus and reduced-motion behavior
- No horizontal overflow at 320, 375, 768, and 1440 CSS pixels
- No browser-console errors on the main routes
- Copy review against the approved source documents and confidentiality boundary
- Production-equivalent Django deployment checks and Vercel configuration validation

## Out of Scope

- Executing a Vercel deployment or changing Vercel Project Settings
- Choosing or configuring a custom domain
- Production database setup
- CMS or admin content editing
- Contact-form delivery
- Analytics and tracking
- Blog, search, accounts, or localization
- Résumé generation or download
- Dark theme
