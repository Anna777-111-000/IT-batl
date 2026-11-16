import io
import base64
import qrcode

from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.db.models import Count
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from .models import BattleEvent, Submission, Vote


def battle_list(request):
    battles = BattleEvent.objects.all()
    return render(request, "battles/battle_list.html", {"battles": battles})


def battle_detail(request, pk):
    battle = get_object_or_404(BattleEvent, pk=pk)
    return render(request, "battles/battle_detail.html", {"battle": battle})


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
                Submission.objects.update_or_create(
                    battle=battle,
                    team=team,
                    defaults={"code_snapshot": code},
                )
                success = True

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


def host_dashboard(request, pk):
    battle = get_object_or_404(BattleEvent, pk=pk)

    # Генерация QR-кода на ссылку голосования
    vote_url = request.build_absolute_uri(
        reverse("battles:vote_page", args=[battle.pk])
    )
    qr = qrcode.make(vote_url)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "battles/host_dashboard.html", {
        "battle": battle,
        "vote_url": vote_url,
        "qr_base64": qr_base64,
    })


def results_fragment(request, pk):
    battle = get_object_or_404(BattleEvent, pk=pk)

    submissions = (
        Submission.objects.filter(battle=battle)
        .select_related("team")
        .annotate(votes_count=Count("votes"))
        .order_by("-votes_count", "team__name")
    )

    formatter = HtmlFormatter(style="monokai", cssclass="highlight")

    rendered_submissions = []
    for sub in submissions:
        code_html = highlight(sub.code_snapshot, PythonLexer(), formatter)
        rendered_submissions.append({
            "team_name": sub.team.name,
            "votes_count": sub.votes_count,
            "code_html": code_html,
        })

    context = {
        "battle": battle,
        "rendered_submissions": rendered_submissions,
        "pygments_css": formatter.get_style_defs(".highlight"),
    }
    return render(request, "battles/partials/results.html", context)


@require_POST
def next_status(request, pk):
    battle = get_object_or_404(BattleEvent, pk=pk)
    order = [
        BattleEvent.Status.WAITING,
        BattleEvent.Status.SUBMISSION,
        BattleEvent.Status.VOTING,
        BattleEvent.Status.FINISHED,
    ]
    try:
        current_idx = order.index(battle.status)
    except ValueError:
        current_idx = 0
    battle.status = order[min(current_idx + 1, len(order) - 1)]
    battle.save()
    return redirect("battles:host_dashboard", pk=pk)


@require_POST
def update_status(request, pk):
    battle = get_object_or_404(BattleEvent, pk=pk)
    new_status = request.POST.get("status")

    if new_status in BattleEvent.Status.values:
        battle.status = new_status
        battle.save()

    return redirect("battles:host_dashboard", pk=pk)