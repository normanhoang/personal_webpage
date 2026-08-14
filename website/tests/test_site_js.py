import shutil
import subprocess
import textwrap
from unittest import TestResult
from unittest.mock import patch

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase


class SiteJavaScriptTests(SimpleTestCase):
    def test_missing_node_skips_the_behavior_harness(self):
        behavior_test = SiteJavaScriptTests(
            "test_escape_only_restores_focus_when_closing_an_open_menu"
        )
        result = TestResult()

        with patch("shutil.which", return_value=None):
            behavior_test.run(result)

        self.assertEqual(result.failures, [])
        self.assertEqual(result.errors, [])
        self.assertEqual(len(result.skipped), 1)
        self.assertIn("Node.js is not installed", result.skipped[0][1])

    def test_escape_only_restores_focus_when_closing_an_open_menu(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is not installed; skipping site.js behavior harness")
        script_path = finders.find("website/js/site.js")
        self.assertIsNotNone(script_path)

        harness = textwrap.dedent(
            """
            const fs = require("fs");
            const vm = require("vm");

            const listeners = {};
            let focusCalls = 0;
            const attributes = new Map([["aria-expanded", "false"]]);
            const classes = new Set();

            const toggle = {
              addEventListener(type, callback) { listeners[`toggle:${type}`] = callback; },
              getAttribute(name) { return attributes.get(name); },
              setAttribute(name, value) { attributes.set(name, value); },
              focus() { focusCalls += 1; },
            };
            const navigation = {
              addEventListener(type, callback) { listeners[`navigation:${type}`] = callback; },
            };
            const document = {
              documentElement: {
                classList: {
                  add(name) { classes.add(name); },
                  remove(name) { classes.delete(name); },
                  toggle(name, force) { force ? classes.add(name) : classes.delete(name); },
                },
              },
              querySelector(selector) {
                if (selector === ".nav-toggle") return toggle;
                if (selector === "#primary-navigation") return navigation;
                return null;
              },
              addEventListener(type, callback) { listeners[`document:${type}`] = callback; },
            };

            vm.runInNewContext(fs.readFileSync(process.argv[1], "utf8"), { document });

            listeners["document:keydown"]({ key: "Escape" });
            if (focusCalls !== 0) {
              throw new Error(`closed menu Escape focused toggle ${focusCalls} time(s)`);
            }

            listeners["toggle:click"]();
            if (attributes.get("aria-expanded") !== "true" || !classes.has("nav-open")) {
              throw new Error("click did not open the menu");
            }

            listeners["document:keydown"]({ key: "Escape" });
            if (attributes.get("aria-expanded") !== "false" || classes.has("nav-open")) {
              throw new Error("open menu Escape did not close the menu");
            }
            if (focusCalls !== 1) {
              throw new Error(`open menu Escape focused toggle ${focusCalls} time(s)`);
            }
            """
        )
        result = subprocess.run(
            [node, "-e", harness, script_path],
            capture_output=True,
            text=True,
            timeout=10,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
