from django.conf import settings
from django.templatetags.static import static

from .content import SITE


def site_metadata(request):
    site_url = settings.SITE_URL.rstrip("/")
    return {
        "site": SITE,
        "site_url": site_url,
        "canonical_url": f"{site_url}{request.path}",
        "meta_title": f"{SITE['name']} · Quantitative Developer",
        "meta_description": SITE["supporting_line"],
        "meta_type": "website",
        "social_image_url": f"{site_url}{static('website/img/social-card.png')}",
        "social_image_alt": (
            "Norman Hoang, Quantitative Developer — Risk, Pricing, and Model Implementation"
        ),
    }
