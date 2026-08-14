import json
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class VercelConfigurationTests(SimpleTestCase):
    def test_vercel_config_applies_strict_headers_without_routing_or_builds(self):
        config_path = Path(settings.BASE_DIR) / "vercel.json"
        self.assertTrue(config_path.exists())
        config = json.loads(config_path.read_text())

        self.assertNotIn("builds", config)
        self.assertNotIn("routes", config)
        self.assertNotIn("rewrites", config)
        self.assertEqual(set(config), {"$schema", "headers"})
        self.assertEqual(len(config["headers"]), 1)
        header_rule = config["headers"][0]
        self.assertEqual(set(header_rule), {"source", "headers"})
        self.assertEqual(header_rule["source"], "/(.*)")

        expected_headers = {
            "Content-Security-Policy": (
                "default-src 'self'; base-uri 'self'; object-src 'none'; "
                "frame-ancestors 'none'; form-action 'self'; img-src 'self' data:; "
                "font-src 'self'; style-src 'self'; script-src 'self'; "
                "connect-src 'self'; upgrade-insecure-requests"
            ),
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        }
        header_items = header_rule["headers"]
        self.assertEqual(len(header_items), len(expected_headers))
        header_names = [item["key"] for item in header_items]
        self.assertEqual(len(header_names), len(set(header_names)))
        self.assertEqual(set(header_names), set(expected_headers))
        self.assertTrue(all(set(item) == {"key", "value"} for item in header_items))
        headers = {item["key"]: item["value"] for item in header_items}
        self.assertEqual(headers, expected_headers)

        expected_csp_directives = [
            "default-src 'self'",
            "base-uri 'self'",
            "object-src 'none'",
            "frame-ancestors 'none'",
            "form-action 'self'",
            "img-src 'self' data:",
            "font-src 'self'",
            "style-src 'self'",
            "script-src 'self'",
            "connect-src 'self'",
            "upgrade-insecure-requests",
        ]
        csp_directives = [
            directive.strip()
            for directive in headers["Content-Security-Policy"].split(";")
        ]
        self.assertEqual(len(csp_directives), len(set(csp_directives)))
        self.assertEqual(csp_directives, expected_csp_directives)

        csp = headers["Content-Security-Policy"]
        self.assertIn("default-src 'self'", csp)
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertNotIn("unsafe-inline", csp)
        self.assertNotIn("http:", csp)
        self.assertNotIn("https:", csp)
