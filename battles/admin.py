from django.contrib import admin
from .models import BattleEvent, Team, Submission, Vote


class TeamInline(admin.TabularInline):
    model = Team
    extra = 1


@admin.register(BattleEvent)
class BattleEventAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "scheduled_at", "created_at")
    list_filter = ("status",)
    search_fields = ("title",)
    inlines = [TeamInline]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "battle", "pin_code")
    list_filter = ("battle",)
    search_fields = ("name",)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("team", "battle", "language", "timestamp")
    list_filter = ("battle", "language")
    readonly_fields = ("timestamp",)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("submission", "score", "session_key", "created_at")
    list_filter = ("submission__battle",)
    readonly_fields = ("created_at",)