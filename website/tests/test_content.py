from django.test import SimpleTestCase

from website.content import CASE_STUDIES, EXPERIENCE, SITE, get_case_study


class ContentContractTests(SimpleTestCase):
    def test_site_identity_and_contact_are_canonical(self):
        self.assertEqual(SITE["name"], "Norman Hoang")
        self.assertEqual(SITE["location"], "New York, NY")
        self.assertEqual(SITE["email"], "normanhoang@gmail.com")
        self.assertEqual(
            SITE["linkedin"], "https://www.linkedin.com/in/normanhoang/"
        )
        self.assertEqual(SITE["github"], "https://github.com/normanhoang/")

    def test_case_studies_have_unique_approved_slugs_and_sections(self):
        self.assertEqual(
            [study["slug"] for study in CASE_STUDIES],
            [
                "risk-calibration",
                "spark-python-modernization",
                "group-lasso",
                "oracle-trino",
            ],
        )
        for study in CASE_STUDIES:
            with self.subTest(slug=study["slug"]):
                self.assertEqual(
                    list(study["sections"]),
                    [
                        "Context",
                        "Problem",
                        "Constraints",
                        "Approach",
                        "Measurable impact",
                    ],
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

    def test_platform_modernization_claims_preserve_scope_and_metrics(self):
        study = get_case_study("spark-python-modernization")
        self.assertIsNotNone(study)

        combined = " ".join(study["sections"].values())
        self.assertEqual(study["title"], "Spark and Python Quant Platform Modernization")
        self.assertIn("Spark 3.5.6", combined)
        self.assertIn("Python 3.12", combined)
        self.assertIn("3–4 months", combined)
        self.assertIn("hundreds", combined)
        self.assertIn("led", combined)
        self.assertIn("built", combined)
        self.assertIn("collabor", combined.lower())

    def test_edwards_role_preserves_official_identity_and_dates(self):
        roles = {
            (role["employer"], role["title"], role["dates"])
            for role in EXPERIENCE
        }
        self.assertIn(
            (
                "Edwards Lifesciences",
                "IT Technician",
                "August 2011–October 2012",
            ),
            roles,
        )
