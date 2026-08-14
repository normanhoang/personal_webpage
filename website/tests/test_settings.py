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

    def test_vercel_silences_only_accepted_hsts_deploy_checks(self):
        result = self._probe(
            "import json; from django.conf import settings; "
            "print(json.dumps(settings.SILENCED_SYSTEM_CHECKS))",
            VERCEL="1",
            DJANGO_SECRET_KEY="test-only-secret-key-with-more-than-fifty-unique-characters-1234567890",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            ["security.W005", "security.W021"],
        )

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

    def test_only_root_private_candidate_instructions_are_git_ignored(self):
        root_result = subprocess.run(
            ["git", "check-ignore", "-q", "CLAUDE.md"],
            cwd=settings.BASE_DIR,
            timeout=10,
        )
        nested_result = subprocess.run(
            ["git", "check-ignore", "-q", "docs/CLAUDE.md"],
            cwd=settings.BASE_DIR,
            timeout=10,
        )

        self.assertEqual(root_result.returncode, 0)
        self.assertEqual(nested_result.returncode, 1)
