from django.urls import path

from . import views


app_name = "website"

urlpatterns = [
    path("", views.home, name="home"),
    path("experience/", views.experience, name="experience"),
    path("case-studies/", views.case_studies, name="case_studies"),
    path("contact/", views.contact, name="contact"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path(
        "case-studies/<slug:slug>/",
        views.case_study_detail,
        name="case_study_detail",
    ),
]
