from django.db import models


class BattleEvent(models.Model):
    """Событие «Баттл» — одно соревнование."""

    class Status(models.TextChoices):
        WAITING = "waiting", "Ожидание"
        SUBMISSION = "submission", "Приём решений"
        VOTING = "voting", "Голосование"
        FINISHED = "finished", "Завершено"

    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True)
    scheduled_at = models.DateTimeField("Дата проведения")
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.WAITING,
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Баттл"
        verbose_name_plural = "Баттлы"
        ordering = ["-scheduled_at"]

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"


class Team(models.Model):
    """Команда-участник конкретного баттла."""

    battle = models.ForeignKey(
        BattleEvent,
        on_delete=models.CASCADE,
        related_name="teams",
        verbose_name="Баттл",
    )
    name = models.CharField("Название команды", max_length=100)
    pin_code = models.CharField("PIN-код", max_length=6, blank=True)

    class Meta:
        verbose_name = "Команда"
        verbose_name_plural = "Команды"
        unique_together = ("battle", "name")

    def __str__(self):
        return f"{self.name} ({self.battle.title})"


class Submission(models.Model):
    """Решение команды. Одно на команду в рамках баттла."""

    battle = models.ForeignKey(
        BattleEvent,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="Баттл",
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="Команда",
    )
    code_snapshot = models.TextField("Код решения")
    language = models.CharField("Язык", max_length=30, default="python")
    timestamp = models.DateTimeField("Время отправки", auto_now=True)

    class Meta:
        verbose_name = "Решение"
        verbose_name_plural = "Решения"
        unique_together = ("battle", "team")

    def __str__(self):
        return f"{self.team.name} → {self.battle.title}"


class Vote(models.Model):
    """Голос зрителя за конкретное решение."""

    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name="votes",
        verbose_name="Решение",
    )
    session_key = models.CharField("Ключ сессии", max_length=64)
    voter_ip = models.GenericIPAddressField("IP голосующего", null=True, blank=True)
    score = models.PositiveSmallIntegerField("Вес голоса", default=1)
    created_at = models.DateTimeField("Когда", auto_now_add=True)

    class Meta:
        verbose_name = "Голос"
        verbose_name_plural = "Голоса"
        unique_together = ("submission", "session_key")

    def __str__(self):
        return f"голос({self.score}) → {self.submission.team.name}"