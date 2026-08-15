import posixpath
import re
import struct
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase
from django.templatetags.static import static
from django.urls import reverse


class _PageContractParser(HTMLParser):
    _void_elements = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self):
        super().__init__()
        self.element_stack = []
        self.navigation_toggle = None
        self.primary_navigation = None
        self.icons = []
        self.risk_surfaces = []
        self.stylesheets = []
        self.scripts = []
        self.proof_ledger_inside_hero = False
        self.proof_item_count = 0
        self._current_surface = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = set(attributes.get("class", "").split())
        ancestor_classes = {
            class_name
            for _, element_classes in self.element_stack
            for class_name in element_classes
        }

        if tag == "dl" and "proof-ledger" in classes:
            self.proof_ledger_inside_hero = "hero" in ancestor_classes
        if "proof-item" in classes:
            self.proof_item_count += 1

        if tag == "button" and "nav-toggle" in classes:
            self.navigation_toggle = attributes
        if tag == "nav" and attributes.get("id") == "primary-navigation":
            self.primary_navigation = attributes
        if tag == "link" and "stylesheet" in attributes.get("rel", "").split():
            self.stylesheets.append(attributes)
        if tag == "link" and "icon" in attributes.get("rel", "").split():
            self.icons.append(attributes)
        if tag == "script" and attributes.get("src"):
            self.scripts.append(attributes)

        if tag == "svg" and "risk-surface" in classes:
            self._current_surface = {
                "attributes": attributes,
                "paths": [],
                "circles": [],
                "text": [],
            }
            self.risk_surfaces.append(self._current_surface)
        elif self._current_surface is not None and tag == "path":
            self._current_surface["paths"].append(attributes)
        elif self._current_surface is not None and tag == "circle":
            self._current_surface["circles"].append(attributes)

        if tag not in self._void_elements:
            self.element_stack.append((tag, classes))

    def handle_endtag(self, tag):
        if tag == "svg":
            self._current_surface = None
        for index in range(len(self.element_stack) - 1, -1, -1):
            if self.element_stack[index][0] == tag:
                del self.element_stack[index:]
                break

    def handle_data(self, data):
        if self._current_surface is not None:
            self._current_surface["text"].append(data)


class StaticAssetTests(SimpleTestCase):
    @staticmethod
    def _static_path(asset):
        path = finders.find(asset)
        if path is None:
            raise AssertionError(f"Static asset is not discoverable: {asset}")
        return Path(path)

    def _page_contract(self, route):
        response = self.client.get(route)
        parser = _PageContractParser()
        parser.feed(response.content.decode())
        return parser

    def test_required_static_assets_are_discoverable(self):
        for path in (
            "website/css/site.css",
            "website/js/site.js",
            "website/fonts/STIXTwoText-Variable.ttf",
            "website/fonts/IBMPlexSans-Variable.ttf",
            "website/fonts/IBMPlexMono-Regular.ttf",
            "website/img/finapp-dashboard-light.png",
            "website/img/model-explainability.png",
            "website/img/social-card.svg",
            "website/img/social-card.png",
        ):
            with self.subTest(path=path):
                self.assertIsNotNone(finders.find(path))

    def test_pages_declare_a_discoverable_local_favicon(self):
        routes = (
            reverse("website:home"),
            reverse(
                "website:case_study_detail", kwargs={"slug": "risk-calibration"}
            ),
        )
        expected_icon = static("website/img/favicon.svg")

        for route in routes:
            with self.subTest(route=route):
                page = self._page_contract(route)
                self.assertEqual(
                    [icon.get("href") for icon in page.icons], [expected_icon]
                )
                self.assertIsNotNone(finders.find("website/img/favicon.svg"))

    def test_home_and_detail_navigation_toggle_controls_the_named_navigation(self):
        routes = (
            reverse("website:home"),
            reverse(
                "website:case_study_detail", kwargs={"slug": "risk-calibration"}
            ),
        )

        for route in routes:
            with self.subTest(route=route):
                page = self._page_contract(route)
                self.assertIsNotNone(page.navigation_toggle)
                self.assertIsNotNone(page.primary_navigation)
                self.assertEqual(page.navigation_toggle.get("type"), "button")
                self.assertEqual(page.navigation_toggle.get("aria-expanded"), "false")
                self.assertEqual(
                    page.navigation_toggle.get("aria-controls"),
                    page.primary_navigation.get("id"),
                )
                self.assertEqual(
                    page.primary_navigation.get("aria-label"), "Primary navigation"
                )

    def test_home_and_detail_load_the_exact_local_css_and_deferred_javascript(self):
        routes = (
            reverse("website:home"),
            reverse(
                "website:case_study_detail", kwargs={"slug": "risk-calibration"}
            ),
        )
        expected_stylesheet = static("website/css/site.css")
        expected_script = static("website/js/site.js")

        for route in routes:
            with self.subTest(route=route):
                page = self._page_contract(route)
                self.assertEqual(
                    [link.get("href") for link in page.stylesheets],
                    [expected_stylesheet],
                )
                self.assertEqual(
                    [script.get("src") for script in page.scripts], [expected_script]
                )
                self.assertIn("defer", page.scripts[0])

    def test_home_proof_ledger_is_part_of_the_hero_composition(self):
        page = self._page_contract(reverse("website:home"))

        self.assertTrue(page.proof_ledger_inside_hero)
        self.assertEqual(page.proof_item_count, 3)

    def test_home_and_detail_risk_surfaces_are_complete_decorative_graphics(self):
        routes = (
            reverse("website:home"),
            reverse(
                "website:case_study_detail", kwargs={"slug": "risk-calibration"}
            ),
        )

        for route in routes:
            with self.subTest(route=route):
                page = self._page_contract(route)
                self.assertEqual(len(page.risk_surfaces), 1)
                surface = page.risk_surfaces[0]
                self.assertEqual(surface["attributes"].get("aria-hidden"), "true")
                self.assertEqual(surface["attributes"].get("focusable"), "false")
                self.assertEqual(surface["attributes"].get("viewbox"), "0 0 640 540")
                self.assertEqual(len(surface["paths"]), 5)
                self.assertEqual(
                    sum(
                        "risk-surface__signal"
                        in path.get("class", "").split()
                        for path in surface["paths"]
                    ),
                    1,
                )
                self.assertEqual(len(surface["circles"]), 1)
                self.assertIn(
                    "risk-surface__point",
                    surface["circles"][0].get("class", "").split(),
                )
                self.assertFalse("".join(surface["text"]).strip())

    def test_finapp_image_uses_source_pixel_dimensions(self):
        response = self.client.get(reverse("website:home"))
        self.assertContains(response, 'width="1242"')
        self.assertContains(response, 'height="2688"')

    def test_stylesheet_only_uses_the_approved_palette(self):
        css = self._static_path("website/css/site.css").read_text()
        approved = {
            "#f5f7fa",
            "#14213d",
            "#2457c5",
            "#b5683a",
            "#d5dce5",
            "#5c6675",
        }
        used = {
            value.lower() for value in re.findall(r"#[0-9a-fA-F]{3,8}\b", css)
        }
        self.assertEqual(used - approved, set())

    def test_runtime_css_and_javascript_do_not_load_external_resources(self):
        css = self._static_path("website/css/site.css").read_text()
        javascript = self._static_path("website/js/site.js").read_text()
        external_url = re.compile(r"(?i)(?:https?:)?//")

        css_urls = [
            value.strip(" \t\"'")
            for value in re.findall(r"url\(([^)]+)\)", css, flags=re.IGNORECASE)
        ]
        css_imports = [
            value.strip(" \t\"'")
            for value in re.findall(
                r"@import\s+(?:url\()?\s*([^);\s]+)", css, flags=re.IGNORECASE
            )
        ]
        self.assertTrue(css_urls)
        self.assertFalse(
            [value for value in css_urls + css_imports if external_url.match(value)]
        )
        self.assertIsNone(external_url.search(javascript))

    def test_every_relative_stylesheet_url_resolves_through_staticfiles(self):
        stylesheet_asset = "website/css/site.css"
        css = self._static_path(stylesheet_asset).read_text()
        css_urls = [
            value.strip(" \t\"'")
            for value in re.findall(r"url\(([^)]+)\)", css, flags=re.IGNORECASE)
        ]
        self.assertTrue(css_urls)

        for reference in css_urls:
            parsed = urlsplit(reference)
            if parsed.scheme or parsed.netloc or reference.startswith("//"):
                continue
            if not parsed.path:
                continue
            resolved_asset = posixpath.normpath(
                posixpath.join(
                    posixpath.dirname(stylesheet_asset), unquote(parsed.path)
                )
            )
            with self.subTest(reference=reference, resolved_asset=resolved_asset):
                self.assertFalse(resolved_asset.startswith("../"))
                self.assertIsNotNone(finders.find(resolved_asset))

    def test_font_licenses_are_bundled_and_nonempty(self):
        for asset in (
            "website/fonts/OFL-STIXTwoText.txt",
            "website/fonts/OFL-IBMPlex.txt",
        ):
            with self.subTest(asset=asset):
                license_text = self._static_path(asset).read_text()
                self.assertGreater(len(license_text), 4_000)
                self.assertIn("SIL Open Font License", license_text)

    def test_font_files_have_valid_sfnt_signatures_and_nontrivial_sizes(self):
        valid_sfnt_signatures = {b"\x00\x01\x00\x00", b"OTTO", b"true", b"typ1"}
        for asset in (
            "website/fonts/STIXTwoText-Variable.ttf",
            "website/fonts/IBMPlexSans-Variable.ttf",
            "website/fonts/IBMPlexMono-Regular.ttf",
        ):
            with self.subTest(asset=asset):
                font_data = self._static_path(asset).read_bytes()
                self.assertGreater(len(font_data), 100_000)
                self.assertIn(font_data[:4], valid_sfnt_signatures)

    def test_finapp_png_has_valid_signature_and_source_dimensions(self):
        image_data = self._static_path(
            "website/img/finapp-dashboard-light.png"
        ).read_bytes()
        self.assertGreater(len(image_data), 100_000)
        self.assertEqual(image_data[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">I", image_data[8:12])[0], 13)
        self.assertEqual(image_data[12:16], b"IHDR")
        self.assertEqual(struct.unpack(">II", image_data[16:24]), (1242, 2688))

    def test_model_explainability_png_has_valid_signature_and_dimensions(self):
        image_data = self._static_path(
            "website/img/model-explainability.png"
        ).read_bytes()

        self.assertGreater(len(image_data), 50_000)
        self.assertLess(len(image_data), 250_000)
        self.assertEqual(image_data[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(image_data[12:16], b"IHDR")
        self.assertEqual(struct.unpack(">II", image_data[16:24]), (1536, 1024))

    def test_social_card_is_discoverable_png_with_share_dimensions(self):
        image_path = self._static_path("website/img/social-card.png")
        image_data = image_path.read_bytes()

        self.assertEqual(image_data[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(image_data[12:16], b"IHDR")
        self.assertEqual(struct.unpack(">II", image_data[16:24]), (1200, 630))
        self.assertIsNotNone(finders.find("website/img/social-card.svg"))

    def test_social_card_source_has_approved_dimensions_and_visible_copy(self):
        source_path = self._static_path("website/img/social-card.svg")
        root = ElementTree.parse(source_path).getroot()
        namespace = {"svg": "http://www.w3.org/2000/svg"}
        visible_copy = [
            "".join(element.itertext()).strip()
            for element in root.findall("svg:text", namespace)
        ]

        self.assertEqual(root.attrib["width"], "1200")
        self.assertEqual(root.attrib["height"], "630")
        self.assertEqual(root.attrib["viewBox"], "0 0 1200 630")
        self.assertEqual(
            visible_copy,
            [
                "Norman Hoang",
                "Quantitative Developer",
                "Risk · Pricing · Model Implementation",
            ],
        )
