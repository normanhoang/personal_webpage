from django.urls import include, path


handler404 = "website.views.page_not_found"
handler500 = "website.views.server_error"


urlpatterns = [
    path("", include("website.urls")),
]
