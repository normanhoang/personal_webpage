# Responsive Review

- Date: 2026-08-14
- Browser: Google Chrome 151.0.7922.138 (headless)
- Server: Django development server with temporary verification-only settings using `DEBUG=False`, production canonical origin `https://norman-portfolio.vercel.app`, and static serving enabled for local inspection

## Automated gate

The complete pre-browser gate passed:

- `.venv/bin/python -m pip check` — no broken requirements
- `.venv/bin/python manage.py check` — no issues
- `.venv/bin/python manage.py test --verbosity 1` — 52 tests passed
- `.venv/bin/python manage.py collectstatic --noinput --dry-run` — 11 static files discovered
- `node --check website/static/website/js/site.js` — passed
- `python -m json.tool vercel.json` — passed
- Production-equivalent `manage.py check --deploy` with Vercel environment variables — no issues or warnings; the two accepted HSTS policy checks were explicitly silenced by the production settings
- `git diff --check` — passed
- `git check-ignore -q CLAUDE.md` — passed

## Browser matrix

The following HTML routes were checked at 320×568, 375×812, 768×1024, and 1440×1200 CSS pixels, for 36 route/viewport combinations:

- `/`
- `/experience/`
- `/case-studies/`
- `/case-studies/risk-calibration/`
- `/case-studies/spark-python-modernization/`
- `/case-studies/group-lasso/`
- `/case-studies/oracle-trino/`
- `/contact/`
- `/missing-page/` with `DEBUG=False`

All 36 combinations passed the following checks:

- `document.documentElement.scrollWidth <= innerWidth`
- All local images decoded and IBM Plex Sans, IBM Plex Mono, and STIX Two Text loaded
- No JavaScript exceptions, request failures, unexpected console errors, or external runtime requests; Chrome's expected main-document HTTP diagnostic for the intentional 404 was not treated as an application error
- Every page rendered its absolute `https://norman-portfolio.vercel.app/...` canonical URL and absolute production social-card URL
- Reduced motion left no animated element or contour animation running
- The 404 response retained status 404 and rendered the branded `Page not found` heading

At both mobile widths, every HTML route also passed menu open, close-by-link, close-with-Escape, and focus-restoration checks, for 18 interaction runs.

`/robots.txt` and `/sitemap.xml` were checked separately. Both returned 200; the crawler policy points to the absolute production sitemap, and the sitemap contains Home, Experience, Case Studies, Contact, and all four case-study detail URLs.

The 500 page was exercised through a temporary verification-only URL module that deliberately raised an exception while `DEBUG=False`; no production diagnostic route was added. It returned status 500 and rendered the branded `Page unavailable` heading, shared layout, canonical URL, and social image at 375×812 and 1440×1200.

## Reproducing the browser run

Prerequisites are the repository's populated `.venv`, Node 24 or newer, and Google Chrome. The fenced sources below are the exact temporary files used by the run. From the repository root, extract them with the documented commands; do not add them to Git.

<!-- verification-settings:start -->
```python
from portfolio.settings import *  # noqa: F403

DEBUG = False
ROOT_URLCONF = "verification_urls"
SECURE_SSL_REDIRECT = False
SITE_URL = "https://norman-portfolio.vercel.app"
```
<!-- verification-settings:end -->

The synthetic route below exists only in the temporary URL module and must never be added to `portfolio/urls.py`:

<!-- verification-urls:start -->
```python
from django.urls import path

from portfolio.urls import handler404, handler500, urlpatterns


def verification_error(request):
    raise RuntimeError("Intentional browser-verification error")


urlpatterns = [
    path("__verification/500/", verification_error),
	*urlpatterns,
]
```
<!-- verification-urls:end -->

Extract the two Python modules:

```bash
awk '/^<!-- verification-settings:start -->$/{copy=1;next} /^<!-- verification-settings:end -->$/{copy=0} copy && !/^```/{print}' \
  docs/verification/responsive-review.md > verification_settings.py
awk '/^<!-- verification-urls:start -->$/{copy=1;next} /^<!-- verification-urls:end -->$/{copy=0} copy && !/^```/{print}' \
  docs/verification/responsive-review.md > verification_urls.py
```

Start the verification server in one terminal:

```bash
.venv/bin/python manage.py runserver 127.0.0.1:8765 \
  --noreload --insecure --settings=verification_settings
```

In a second terminal, create an ephemeral profile and start the same headless Chrome surface used for this review:

```bash
mkdir -p /tmp/resume-website-verification-2026-08-14/chrome-profile
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new \
  --remote-debugging-port=9222 \
  '--remote-allow-origins=*' \
  --user-data-dir=/tmp/resume-website-verification-2026-08-14/chrome-profile \
  --no-first-run \
  --no-default-browser-check \
  --disable-background-networking \
  --disable-component-update \
  --disable-default-apps \
  --disable-extensions \
  --disable-sync \
  --metrics-recording-only \
  about:blank
```

The verification harness is intentionally temporary rather than application code. This is its complete source:

<!-- browser-harness:start -->
```javascript
import fs from "node:fs";

const port = 9222;
const baseUrl = "http://127.0.0.1:8765";
const productionUrl = "https://norman-portfolio.vercel.app";
const outputDir = "/tmp/resume-website-verification-2026-08-14";

const routes = [
  "/",
  "/experience/",
  "/case-studies/",
  "/case-studies/risk-calibration/",
  "/case-studies/spark-python-modernization/",
  "/case-studies/group-lasso/",
  "/case-studies/oracle-trino/",
  "/contact/",
  "/missing-page/",
];
const viewports = [
  { width: 320, height: 568 },
  { width: 375, height: 812 },
  { width: 768, height: 1024 },
  { width: 1440, height: 1200 },
];
const captureRoutes = new Map([
  ["/", "home"],
  ["/contact/", "contact"],
  ["/case-studies/", "case-studies"],
  ["/case-studies/spark-python-modernization/", "spark-python"],
  ["/missing-page/", "404"],
  ["/__verification/500/", "500"],
]);

fs.mkdirSync(outputDir, { recursive: true });

const targets = await fetch(`http://127.0.0.1:${port}/json/list`).then((response) =>
  response.json(),
);
const target = targets.find((item) => item.type === "page");
if (!target) throw new Error("No Chrome page target available");

const socket = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  socket.addEventListener("open", resolve, { once: true });
  socket.addEventListener("error", reject, { once: true });
});

let nextId = 1;
const pending = new Map();
const listeners = new Map();
socket.addEventListener("message", ({ data }) => {
  const message = JSON.parse(data);
  if (message.id) {
    const operation = pending.get(message.id);
    if (!operation) return;
    pending.delete(message.id);
    if (message.error) operation.reject(new Error(JSON.stringify(message.error)));
    else operation.resolve(message.result);
    return;
  }
  for (const callback of listeners.get(message.method) || []) {
    callback(message.params);
  }
});

function send(method, params = {}) {
  const id = nextId++;
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
    socket.send(JSON.stringify({ id, method, params }));
  });
}

function once(method, timeoutMs = 15000) {
  return new Promise((resolve, reject) => {
    const callbacks = listeners.get(method) || [];
    const timer = setTimeout(() => {
      listeners.set(
        method,
        callbacks.filter((callback) => callback !== handler),
      );
      reject(new Error(`Timed out waiting for ${method}`));
    }, timeoutMs);
    const handler = (params) => {
      clearTimeout(timer);
      listeners.set(
        method,
        callbacks.filter((callback) => callback !== handler),
      );
      resolve(params);
    };
    callbacks.push(handler);
    listeners.set(method, callbacks);
  });
}

async function evaluate(expression, awaitPromise = false) {
  const result = await send("Runtime.evaluate", {
    expression,
    awaitPromise,
    returnByValue: true,
  });
  if (result.exceptionDetails) {
    throw new Error(
      result.exceptionDetails.exception?.description || "Evaluation failed",
    );
  }
  return result.result.value;
}

const browserVersion = await send("Browser.getVersion");
await Promise.all([
  send("Page.enable"),
  send("Runtime.enable"),
  send("Network.enable"),
  send("Log.enable"),
]);

let pageExceptions = [];
let consoleErrors = [];
let logErrors = [];
let failedRequests = [];
let requestUrls = [];
let documentStatus = null;
listeners.set("Runtime.exceptionThrown", [({ exceptionDetails }) =>
  pageExceptions.push(exceptionDetails.text),
]);
listeners.set("Runtime.consoleAPICalled", [({ type, args }) => {
  if (type === "error" || type === "assert") {
    consoleErrors.push(
      args.map((argument) => argument.value || argument.description).join(" "),
    );
  }
}]);
listeners.set("Log.entryAdded", [({ entry }) => {
  if (entry.level === "error") logErrors.push(entry.text);
}]);
listeners.set("Network.loadingFailed", [
  ({ blockedReason, canceled, errorText, requestId }) => {
    if (!canceled) {
      failedRequests.push({ blockedReason, errorText, requestId });
    }
  },
]);
listeners.set("Network.requestWillBeSent", [({ request }) =>
  requestUrls.push(request.url),
]);
listeners.set("Network.responseReceived", [({ response, type }) => {
  if (type === "Document") documentStatus = response.status;
}]);

async function setViewport(viewport) {
  await send("Emulation.setDeviceMetricsOverride", {
    width: viewport.width,
    height: viewport.height,
    deviceScaleFactor: 1,
    mobile: viewport.width < 768,
    screenWidth: viewport.width,
    screenHeight: viewport.height,
  });
}

async function navigate(path) {
  pageExceptions = [];
  consoleErrors = [];
  logErrors = [];
  failedRequests = [];
  requestUrls = [];
  documentStatus = null;
  const loaded = once("Page.loadEventFired");
  await send("Page.navigate", { url: `${baseUrl}${path}` });
  await loaded;
  await new Promise((resolve) => setTimeout(resolve, 250));
  await evaluate(`(async () => {
    await document.fonts.ready;
    const images = Array.from(document.images);
    for (const image of images) image.loading = "eager";
    await Promise.race([
      Promise.all(images.map((image) => image.decode().catch(() => undefined))),
      new Promise((resolve) => setTimeout(resolve, 5000)),
    ]);
    return true;
  })()`, true);
  await new Promise((resolve) => setTimeout(resolve, 100));
}

async function pageFacts() {
  return evaluate(`(() => ({
    overflow: document.documentElement.scrollWidth <= innerWidth,
    scrollWidth: document.documentElement.scrollWidth,
    innerWidth,
    images: Array.from(document.images, (image) => ({
      src: image.currentSrc,
      complete: image.complete,
      width: image.naturalWidth,
      height: image.naturalHeight,
    })),
    fonts: {
      status: document.fonts.status,
      plexSans: document.fonts.check('16px "IBM Plex Sans"'),
      plexMono: document.fonts.check('16px "IBM Plex Mono"'),
      stix: document.fonts.check('16px "STIX Two Text"'),
    },
    canonical: document.querySelector('link[rel="canonical"]')?.href,
    socialImage: document.querySelector('meta[property="og:image"]')?.content,
    heading: document.querySelector('h1')?.textContent.trim(),
  }))()`);
}

async function mobileMenuFacts() {
  return evaluate(`(async () => {
    const toggle = document.querySelector('.nav-toggle');
    const navigation = document.querySelector('#primary-navigation');
    const link = navigation.querySelector('a');
    toggle.click();
    const opened = toggle.getAttribute('aria-expanded') === 'true' &&
      document.documentElement.classList.contains('nav-open');
    link.addEventListener('click', (event) => event.preventDefault(), {
      once: true,
    });
    link.click();
    const closedByLink = toggle.getAttribute('aria-expanded') === 'false' &&
      !document.documentElement.classList.contains('nav-open');
    toggle.click();
    toggle.focus();
    document.dispatchEvent(new KeyboardEvent('keydown', {
      key: 'Escape',
      bubbles: true,
    }));
    const closedByEscape = toggle.getAttribute('aria-expanded') === 'false' &&
      !document.documentElement.classList.contains('nav-open');
    const focusRestored = document.activeElement === toggle;
    return { opened, closedByLink, closedByEscape, focusRestored };
  })()`, true);
}

async function reducedMotionFacts() {
  await send("Emulation.setEmulatedMedia", {
    features: [{ name: "prefers-reduced-motion", value: "reduce" }],
  });
  const facts = await evaluate(`(() => ({
    animatedElements: Array.from(document.querySelectorAll('*')).filter(
      (element) => {
        const style = getComputedStyle(element);
        return style.animationName !== 'none' && style.animationDuration !== '0s';
      },
    ).length,
    contourAnimations: Array.from(
      document.querySelectorAll('.risk-surface path'),
      (element) => getComputedStyle(element).animationName,
    ),
  }))()`);
  await send("Emulation.setEmulatedMedia", { features: [] });
  return facts;
}

async function capture(path, name, viewport) {
  await setViewport(viewport);
  await navigate(path);
  const metrics = await send("Page.getLayoutMetrics");
  const size = metrics.cssContentSize;
  const screenshot = await send("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: true,
    fromSurface: true,
    clip: { x: 0, y: 0, width: size.width, height: size.height, scale: 1 },
  });
  const suffix = viewport.width === 375
    ? "mobile-375x812"
    : "desktop-1440x1200";
  const file = `${outputDir}/${name}-${suffix}.png`;
  fs.writeFileSync(file, Buffer.from(screenshot.data, "base64"));
  return file;
}

const matrix = [];
for (const viewport of viewports) {
  await setViewport(viewport);
  for (const route of routes) {
    await navigate(route);
    const facts = await pageFacts();
    const menu = viewport.width <= 375 ? await mobileMenuFacts() : null;
    const motion = await reducedMotionFacts();
    const externalRequests = requestUrls.filter((url) =>
      !url.startsWith(baseUrl) &&
      !url.startsWith("data:") &&
      !url.startsWith("blob:"),
    );
    const expectedStatus = route === "/missing-page/" ? 404 : 200;
    const expectedCanonical = `${productionUrl}${route}`;
    const expectedSocial =
      `${productionUrl}/static/website/img/social-card.png`;
    const unexpectedLogs = logErrors.filter((message) =>
      !(expectedStatus === 404 && message.includes("status of 404")),
    );
    const assertions = {
      status: documentStatus === expectedStatus,
      overflow: facts.overflow,
      images: facts.images.every((image) =>
        image.complete && image.width > 0 && image.height > 0,
      ),
      fonts: facts.fonts.status === "loaded" &&
        facts.fonts.plexSans && facts.fonts.plexMono && facts.fonts.stix,
      console: pageExceptions.length === 0 &&
        consoleErrors.length === 0 && unexpectedLogs.length === 0,
      requests: failedRequests.length === 0,
      external: externalRequests.length === 0,
      canonical: facts.canonical === expectedCanonical,
      socialImage: facts.socialImage === expectedSocial,
      menu: menu === null || Object.values(menu).every(Boolean),
      reducedMotion: motion.animatedElements === 0 &&
        motion.contourAnimations.every((name) => name === "none"),
      branded404: route !== "/missing-page/" ||
        facts.heading === "Page not found",
    };
    matrix.push({
      route,
      viewport,
      status: documentStatus,
      facts,
      menu,
      motion,
      externalRequests,
      failedRequests,
      pageExceptions,
      consoleErrors,
      logErrors,
      assertions,
    });
  }
}

const discovery = [];
for (const path of ["/robots.txt", "/sitemap.xml"]) {
  await setViewport({ width: 1440, height: 1200 });
  await navigate(path);
  const content = await evaluate("document.body.innerText");
  discovery.push({ path, status: documentStatus, content });
}

const error500 = [];
for (const viewport of [
  { width: 375, height: 812 },
  { width: 1440, height: 1200 },
]) {
  await setViewport(viewport);
  await navigate("/__verification/500/");
  const facts = await pageFacts();
  error500.push({
    viewport,
    status: documentStatus,
    heading: facts.heading,
    canonical: facts.canonical,
    socialImage: facts.socialImage,
    consoleErrors,
    failedRequests,
  });
}

const screenshots = [];
for (const [path, name] of captureRoutes) {
  screenshots.push(await capture(path, name, { width: 375, height: 812 }));
  screenshots.push(
    await capture(path, name, { width: 1440, height: 1200 }),
  );
}

const failures = matrix.filter((entry) =>
  Object.values(entry.assertions).some((passed) => !passed),
);
const robots = discovery.find((entry) => entry.path === "/robots.txt");
const sitemap = discovery.find((entry) => entry.path === "/sitemap.xml");
const discoveryPassed = discovery.every((entry) => entry.status === 200) &&
  robots.content.includes(`${productionUrl}/sitemap.xml`) &&
  routes.slice(0, 8).every((route) =>
    sitemap.content.includes(`${productionUrl}${route}`),
  );
const error500Passed = error500.every((entry) =>
  entry.status === 500 &&
  entry.heading === "Page unavailable" &&
  entry.canonical === `${productionUrl}/__verification/500/` &&
  entry.socialImage ===
    `${productionUrl}/static/website/img/social-card.png` &&
  entry.consoleErrors.length === 0 &&
  entry.failedRequests.length === 0,
);

const report = {
  browser: browserVersion.product,
  userAgent: browserVersion.userAgent,
  matrix,
  failures,
  discovery,
  discoveryPassed,
  error500,
  error500Passed,
  screenshots,
};
fs.writeFileSync(
  `${outputDir}/browser-report.json`,
  JSON.stringify(report, null, 2),
);
console.log(JSON.stringify({
  browser: report.browser,
  matrixChecks: matrix.length,
  mobileInteractionRuns: matrix.filter((entry) => entry.menu !== null).length,
  failures: failures.length,
  discoveryPassed,
  error500Passed,
  screenshots: screenshots.length,
  output: `${outputDir}/browser-report.json`,
}, null, 2));
socket.close();
if (failures.length || !discoveryPassed || !error500Passed) {
  process.exitCode = 1;
}
```
<!-- browser-harness:end -->

Extract the fenced harness source and validate its syntax:

```bash
awk '/^<!-- browser-harness:start -->$/{copy=1;next} /^<!-- browser-harness:end -->$/{copy=0} copy && !/^```/{print}' \
  docs/verification/responsive-review.md > /tmp/resume-browser-matrix.mjs
node --check /tmp/resume-browser-matrix.mjs
```

With the Django and Chrome processes above still running, execute it:

```bash
node /tmp/resume-browser-matrix.mjs
```

A passing summary must report `matrixChecks: 36`, `mobileInteractionRuns: 18`, `failures: 0`, `discoveryPassed: true`, `error500Passed: true`, and `screenshots: 12`. After the run, stop both processes and remove the temporary files:

```bash
rm verification_settings.py verification_urls.py /tmp/resume-browser-matrix.mjs
git status --short
```

The status output must not list a temporary module or harness before accepting the evidence.

## Screenshot evidence

Fresh full-page captures were saved outside the repository under `/tmp/resume-website-verification-2026-08-14/`:

- `home-mobile-375x812.png`
- `home-desktop-1440x1200.png`
- `contact-mobile-375x812.png`
- `contact-desktop-1440x1200.png`
- `case-studies-mobile-375x812.png`
- `case-studies-desktop-1440x1200.png`
- `spark-python-mobile-375x812.png`
- `spark-python-desktop-1440x1200.png`
- `404-mobile-375x812.png`
- `404-desktop-1440x1200.png`
- `500-mobile-375x812.png`
- `500-desktop-1440x1200.png`

Visual inspection of all 12 captures passed. Home preserves the proof-led hierarchy and complete Independent Work content; Contact keeps the email and professional-profile links in proportion; the Case Studies index shows all four cards with intact mobile navigation; the Spark/Python detail preserves its section sequence and contour graphic; and the 404/500 pages remain branded, legible, and restrained. No capture showed clipped text, overlap, missing controls, unreadable type, broken imagery, or missing footer content.

The social card was inspected separately at its original 1200×630 resolution. Its typography, contour line, and approved `Norman Hoang`, `Quantitative Developer`, and `Risk · Pricing · Model Implementation` copy are crisp and unclipped.

The machine-readable browser results are in `/tmp/resume-website-verification-2026-08-14/browser-report.json`. These `/tmp` artifacts are ephemeral verification evidence and are not repository assets.

## External verification pending

No deployment or Vercel Project Settings change was made. The following checks require a future push or deployment and remain pending:

- The GitHub Actions workflow run on GitHub
- Vercel framework auto-detection and build completion
- Production and Preview environment-variable configuration
- Response security headers on a Vercel Preview, including compatibility with the Preview Toolbar setting
- Public static/CDN delivery, canonical origin, crawler routes, branded errors, and third-party social unfurl behavior on the deployed URL
