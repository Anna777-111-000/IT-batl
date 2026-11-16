from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import BattleEvent, Submission, Vote


def battle_list(request):
    battles = BattleEvent.objects.all()
    return render(request, "battles/battle_list.html", {"battles": battles})

def battle_detail(request, pk):
    return HttpResponse(f"Баттл #{pk} (заглушка)")

def submission_form(request, pk):
    battle = get_object_or_404(BattleEvent, pk=pk)
    error = None
    success = False

    if request.method == "POST":
        if battle.status != BattleEvent.Status.SUBMISSION:
            error = "Приём решений сейчас закрыт."
        else:
            team_id = request.POST.get("team")
            code = request.POST.get("code", "").strip()

            if not team_id or not code:
                error = "Выберите команду и вставьте код."
            else:
                team = get_object_or_404(battle.teams, pk=team_id)
                submission, created = Submission.objects.update_or_create(
                    battle=battle,
                    team=team,
                    defaults={"code_snapshot": code},
                )
                success = True

    # какие команды уже отправили — пометим в select
    submitted_team_ids = set(
        Submission.objects.filter(battle=battle).values_list("team_id", flat=True)
    )

    return render(
        request,
        "battles/submission_form.html",
        {
            "battle": battle,
            "teams": battle.teams.all(),
            "submitted_team_ids": submitted_team_ids,
            "error": error,
            "success": success,
        },
    )




def vote_page(request, pk):
    battle = get_object_or_404(BattleEvent, pk=pk)
    submissions = (
        Submission.objects.filter(battle=battle)
        .select_related("team")
        .order_by("team__name")
    )

    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    voted_ids = set(
        Vote.objects.filter(
            submission__battle=battle, session_key=session_key
        ).values_list("submission_id", flat=True)
    )

    return render(
        request,
        "battles/vote_page.html",
        {
            "battle": battle,
            "submissions": submissions,
            "voted_ids": voted_ids,
            "already_voted": bool(voted_ids),
        },
    )


def host_dashboard(request, pk):
    return HttpResponse(f"Проектор баттла #{pk} (заглушка)")


@require_POST
def cast_vote(request, submission_id):
    submission = get_object_or_404(
        Submission.objects.select_related("battle", "team"), pk=submission_id
    )
    battle = submission.battle

    if battle.status != BattleEvent.Status.VOTING:
        return HttpResponseForbidden("Голосование закрыто")

    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key

    # один голос с устройства на весь баттл
    already_voted_in_battle = Vote.objects.filter(
        submission__battle=battle, session_key=session_key
    ).exists()

    if not already_voted_in_battle:
        Vote.objects.create(
            submission=submission,
            session_key=session_key,
            voter_ip=request.META.get("REMOTE_ADDR"),
            score=1,
        )

    return render(
        request,
        "battles/partials/vote_button.html",
        {"submission": submission, "voted": True},
    )


def results_fragment(request, pk):
    return HttpResponse(f"Результаты баттла #{pk} (заглушка)")