from django.conf import settings
from django.http import Http404
from django.urls import reverse
from django.shortcuts import render

from .content import (
    ACADEMIC_PROJECTS,
    CASE_STUDIES,
    CREDENTIALS,
    EDUCATION,
    EXPERIENCE,
    INDEPENDENT_WORK,
    LEADERSHIP,
    PROOF_POINTS,
    SITE,
    SKILL_GROUPS,
    get_case_study,
)


def _abbreviate_date_range(date_range):
    def abbreviate(value):
        month_and_year = value.split(" ", 1)
        if len(month_and_year) == 1:
            return value.title()
        return f"{month_and_year[0][:3]} {month_and_year[1]}"

    start, end = date_range.split("–", 1)
    return f"{abbreviate(start)}—{abbreviate(end)}"


def home(request):
    return render(
        request,
        "website/home.html",
        {
            "site": SITE,
            "proof_points": PROOF_POINTS,
            "skill_groups": SKILL_GROUPS,
            "case_studies": CASE_STUDIES,
            "independent_work": INDEPENDENT_WORK,
            "meta_title": "Norman Hoang · Quantitative Developer",
            "meta_description": (
                "Quantitative Developer specializing in model implementation, regulatory "
                "analytics, and production-scale data engineering for banking."
            ),
        },
    )


def experience(request):
    presented_experience = tuple(
        {**role, "display_dates": _abbreviate_date_range(role["dates"])}
        for role in EXPERIENCE
    )
    return render(
        request,
        "website/experience.html",
        {
            "site": SITE,
            "experience": presented_experience,
            "education": EDUCATION,
            "academic_projects": ACADEMIC_PROJECTS,
            "credentials": CREDENTIALS,
            "leadership": LEADERSHIP,
            "meta_title": "Experience · Norman Hoang",
            "meta_description": (
                "Professional experience in quantitative finance, model implementation, risk "
                "analytics, and production-scale data engineering."
            ),
        },
    )


def case_studies(request):
    return render(
        request,
        "website/case_studies.html",
        {
            "site": SITE,
            "case_studies": CASE_STUDIES,
            "meta_title": "Case Studies · Norman Hoang",
            "meta_description": (
                "Case studies in financial risk calibration, quantitative platform "
                "engineering, model implementation, and production-scale data engineering."
            ),
        },
    )


def contact(request):
    return render(
        request,
        "website/contact.html",
        {
            "site": SITE,
            "meta_title": "Contact · Norman Hoang",
            "meta_description": (
                "Contact Norman Hoang about quantitative development, risk and pricing "
                "systems, and banking technology."
            ),
        },
    )


def robots_txt(request):
    return render(
        request,
        "website/robots.txt",
        content_type="text/plain; charset=utf-8",
    )


def sitemap_xml(request):
    paths = (
        reverse("website:home"),
        reverse("website:experience"),
        reverse("website:case_studies"),
        reverse("website:contact"),
        *(
            reverse("website:case_study_detail", kwargs={"slug": study["slug"]})
            for study in CASE_STUDIES
        ),
    )
    return render(
        request,
        "website/sitemap.xml",
        {"urls": tuple(f"{settings.SITE_URL}{path}" for path in paths)},
        content_type="application/xml",
    )


def case_study_detail(request, slug):
    study = get_case_study(slug)
    if study is None:
        raise Http404("Case study not found")
    return render(
        request,
        "website/case_study_detail.html",
        {
            "site": SITE,
            "study": study,
            "meta_title": f"{study['title']} · Norman Hoang",
            "meta_description": study["summary"],
            "meta_type": "article",
        },
    )


def page_not_found(request, exception):
    return render(
        request,
        "404.html",
        {
            "meta_title": "Page not found · Norman Hoang",
            "meta_description": "The requested portfolio page could not be found.",
        },
        status=404,
    )


def server_error(request):
    return render(
        request,
        "500.html",
        {
            "meta_title": "Page unavailable · Norman Hoang",
            "meta_description": "The portfolio page could not be loaded.",
        },
        status=500,
    )
