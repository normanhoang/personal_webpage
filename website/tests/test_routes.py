from django.test import SimpleTestCase, override_settings
from django.urls import reverse


class PublicRouteTests(SimpleTestCase):
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
                body.count(f"<loc>https://norman-portfolio.vercel.app{path}</loc>"),
                1,
            )

    def test_primary_pages_render(self):
        for route_name in (
            "website:home",
            "website:experience",
            "website:case_studies",
        ):
            with self.subTest(route_name=route_name):
                self.assertEqual(self.client.get(reverse(route_name)).status_code, 200)

    def test_contact_page_renders(self):
        self.assertEqual(self.client.get("/contact/").status_code, 200)

    def test_each_case_study_route_renders(self):
        for slug in (
            "risk-calibration",
            "spark-python-modernization",
            "group-lasso",
            "oracle-trino",
        ):
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
