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
                self.assertIn(
                    f'<link rel="canonical" href="https://norman-portfolio.vercel.app{route}">',
                    body,
                )
                self.assertIn(f'<meta property="og:title" content="{title}">', body)
                self.assertIn(f'<meta name="description" content="{description}">', body)
                self.assertIn('<meta name="twitter:card" content="summary_large_image">', body)
                self.assertIn(
                    "https://norman-portfolio.vercel.app/static/website/img/social-card.png",
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
            "tooling and the environment used to develop and run it across Global "
            'Risk Analytics.">',
            html=True,
        )
        self.assertContains(
            response,
            f'<meta property="og:url" content="https://norman-portfolio.vercel.app{route}">',
            html=True,
        )
