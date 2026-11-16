from django.urls import path
from . import views

app_name = "battles"

urlpatterns = [
    path("", views.battle_list, name="battle_list"),
    path("battle/<int:pk>/", views.battle_detail, name="battle_detail"),
    path("battle/<int:pk>/submit/", views.submission_form, name="submission_form"),
    path("battle/<int:pk>/vote/", views.vote_page, name="vote_page"),
    path("battle/<int:pk>/host/", views.host_dashboard, name="host_dashboard"),

    # HTMX-эндпоинты
    path("vote/<int:submission_id>/", views.cast_vote, name="cast_vote"),
    path(
        "battle/<int:pk>/results-fragment/",
        views.results_fragment,
        name="results_fragment",
    ),
]