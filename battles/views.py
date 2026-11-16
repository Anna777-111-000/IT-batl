from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import BattleEvent, Submission


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
    return HttpResponse(f"Голосование баттла #{pk} (заглушка)")


def host_dashboard(request, pk):
    return HttpResponse(f"Проектор баттла #{pk} (заглушка)")


def cast_vote(request, submission_id):
    return HttpResponse(f"Голос за решение #{submission_id} (заглушка)")


def results_fragment(request, pk):
    return HttpResponse(f"Результаты баттла #{pk} (заглушка)")