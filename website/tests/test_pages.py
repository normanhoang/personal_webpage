from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import reverse


class RenderedPageTests(SimpleTestCase):
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

    def test_home_renders_positioning_proof_and_footer_contact(self):
        response = self.client.get(reverse("website:home"))
        self.assertContains(
            response, "I build quantitative risk and pricing systems for banking."
        )
        self.assertContains(
            response, "Vice President in Global Risk Analytics at Bank of America"
        )
        self.assertContains(response, "~2B")
        self.assertContains(response, "58 → 119")
        self.assertContains(
            response, "weekly active users of the shared statistical library"
        )
        self.assertContains(response, "IFRS · CECL · CCAR")
        self.assertNotContains(response, "70% / 60%")
        self.assertContains(response, "normanhoang@gmail.com")

    def test_home_renders_curated_independent_work(self):
        response = self.client.get(reverse("website:home"))

        self.assertContains(response, 'class="finapp-feature"', count=1)
        self.assertContains(
            response,
            'class="independent-card independent-card--illustrated"',
            count=1,
        )
        self.assertContains(response, "Mathematics of Model Explainability")
        self.assertContains(
            response,
            '<img class="explainability-image" '
            'src="/static/website/img/model-explainability.png" '
            'alt="Abstract SHAP-style feature contribution plot with cobalt and '
            'copper points distributed around a central baseline" '
            'width="1536" height="1024" loading="lazy">',
            html=True,
        )
        self.assertContains(
            response,
            "An internal, non-peer-reviewed working paper for Model Risk Management "
            "covering XGBoost, SHAP, and feature importance.",
        )
        self.assertNotContains(response, 'id="beyond-work-title"')
        self.assertNotContains(response, "Beyond work, I enjoy")

    def test_contact_page_renders_neutral_direct_contact_options(self):
        response = self.client.get(reverse("website:contact"))

        self.assertContains(response, "Let’s discuss rigorous quantitative systems.")
        self.assertContains(
            response,
            "For conversations about quantitative development, risk and pricing systems,",
        )
        self.assertContains(response, "or banking technology.")
        self.assertContains(response, "New York, NY")
        self.assertContains(
            response,
            '<a class="contact-email" href="mailto:normanhoang@gmail.com">'
            "normanhoang@gmail.com</a>",
            html=True,
        )
        self.assertContains(response, "LinkedIn")
        self.assertContains(response, "GitHub")
        self.assertContains(response, 'target="_blank"', count=3)
        self.assertContains(response, 'rel="noreferrer noopener"', count=3)
        self.assertContains(
            response,
            '<a href="/contact/" aria-current="page">Contact</a>',
            html=True,
        )
        self.assertNotContains(response, "<form")
        self.assertNotContains(response, "open to opportunities")

    def test_public_pages_use_contact_route_and_compact_footer(self):
        routes = (
            reverse("website:home"),
            reverse("website:experience"),
            reverse("website:case_studies"),
            reverse(
                "website:case_study_detail", kwargs={"slug": "risk-calibration"}
            ),
            reverse("website:contact"),
        )

        for route in routes:
            response = self.client.get(route)
            body = response.content.decode()
            footer = body.split('<footer class="site-footer">', 1)[1].split(
                "</footer>", 1
            )[0]
            with self.subTest(route=route):
                self.assertContains(response, 'href="/contact/"')
                self.assertNotContains(response, 'href="/#contact"')
                self.assertNotContains(response, 'id="contact"')
                self.assertIn("mailto:normanhoang@gmail.com", footer)
                self.assertIn("https://www.linkedin.com/in/normanhoang/", footer)
                self.assertNotIn("https://github.com/normanhoang/", footer)

    def test_home_renders_all_capabilities_in_spec_order(self):
        response = self.client.get(reverse("website:home"))
        body = response.content.decode()
        titles = (
            "Risk &amp; regulatory analytics",
            "Quantitative model implementation",
            "Quant platform &amp; data engineering",
            "Risk &amp; pricing technology",
        )

        self.assertEqual(body.count('class="capability-group"'), 4)
        for title in titles:
            self.assertIn(f"<h3>{title}</h3>", body)
        positions = [body.index(f"<h3>{title}</h3>") for title in titles]
        self.assertEqual(positions, sorted(positions))

    def test_group_lasso_pages_render_the_exact_approved_title(self):
        approved_title = "Group Lasso Model Implementation and Runtime Optimization"
        for route in (
            reverse("website:case_studies"),
            reverse(
                "website:case_study_detail", kwargs={"slug": "group-lasso"}
            ),
        ):
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertContains(response, approved_title)

    def test_experience_renders_official_titles_and_canonical_dates(self):
        response = self.client.get(reverse("website:experience"))
        self.assertContains(response, "Vice President, Quantitative Finance Analyst")
        self.assertContains(response, "Jan 2023—Present")
        self.assertContains(
            response, "Assistant Vice President, Quantitative Finance Analyst"
        )
        self.assertContains(response, "Aug 2019—Dec 2022")
        self.assertContains(response, "58 to 119 users")
        self.assertContains(response, "Spark 3.5.6 and Python 3.12")
        self.assertContains(response, "JupyterLab environment used by hundreds")
        self.assertContains(
            response,
            "Hazard Rate, Beta, Trinomial, Inflated Beta, and Bayesian regression",
        )
        self.assertContains(response, "Senior Application Engineer")
        self.assertNotContains(
            response,
            "Senior Application Engineer / Technical Training Support Engineer",
        )
        self.assertContains(response, "M.S. in Quantitative Finance")
        self.assertContains(
            response,
            "B.S. in Electrical Engineering, Specialization in Systems and Signals",
        )
        self.assertContains(response, "C++ Programming")
        self.assertContains(response, "Leadership &amp; community", html=True)
        self.assertContains(
            response, "Led the Global Risk Analytics Knowledge Share program for three years"
        )
        self.assertContains(response, "Jersey City Site Team")
        self.assertContains(response, "Founded and led the employee book club")

    @patch(
        "website.views.EXPERIENCE",
        (
            {
                "employer": "Earlier Employer",
                "title": "Earlier Role",
                "group": "Earlier Group",
                "dates": "March 2004–November 2008",
                "highlights": ("Earlier role evidence.",),
            },
        ),
    )
    def test_experience_abbreviates_dates_for_any_role(self):
        response = self.client.get(reverse("website:experience"))

        self.assertContains(response, "Mar 2004—Nov 2008")

    def test_case_study_index_links_to_all_detail_pages(self):
        response = self.client.get(reverse("website:case_studies"))
        for slug in (
            "risk-calibration",
            "spark-python-modernization",
            "group-lasso",
            "oracle-trino",
        ):
            self.assertContains(
                response,
                reverse("website:case_study_detail", kwargs={"slug": slug}),
            )

    def test_case_detail_uses_shared_section_structure(self):
        response = self.client.get(
            reverse("website:case_study_detail", kwargs={"slug": "group-lasso"})
        )
        for heading in (
            "Context",
            "Problem",
            "Constraints",
            "Approach",
            "Measurable impact",
            "Technologies",
        ):
            self.assertContains(response, heading)

    def test_public_pages_omit_prohibited_personal_and_job_search_content(self):
        for route_name in (
            "website:home",
            "website:experience",
            "website:case_studies",
            "website:contact",
        ):
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
