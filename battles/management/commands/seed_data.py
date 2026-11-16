from django.core.management.base import BaseCommand
from django.utils import timezone
from battles.models import BattleEvent, Team, Submission, Vote


class Command(BaseCommand):
    help = "Наполняет базу тестовыми данными для демонстрации"

    def handle(self, *args, **options):
        self.stdout.write("Очистка старых данных...")
        Vote.objects.all().delete()
        Submission.objects.all().delete()
        Team.objects.all().delete()
        BattleEvent.objects.all().delete()

        self.stdout.write("Создание баттла...")
        battle = BattleEvent.objects.create(
            title="ИТ-баттл #1: FizzBuzz",
            description="Классическая задача на скорость и читаемость кода.",
            scheduled_at=timezone.now(),
            status=BattleEvent.Status.VOTING,
        )

        team_names = ["Альфа", "Бета", "Гамма", "Дельта"]
        teams = []
        for name in team_names:
            team = Team.objects.create(battle=battle, name=name, pin_code="1234")
            teams.append(team)

        self.stdout.write("Добавление решений...")

        # 4 разных решения для демонстрации подсветки
        codes = [
            # Альфа (простой цикл)
            "for i in range(1, 101):\n"
            "    if i % 15 == 0:\n"
            "        print('FizzBuzz')\n"
            "    elif i % 3 == 0:\n"
            "        print('Fizz')\n"
            "    elif i % 5 == 0:\n"
            "        print('Buzz')\n"
            "    else:\n"
            "        print(i)",

            # Бета (генератор списка)
            "def fizzbuzz(n):\n"
            "    return [\n"
            "        'FizzBuzz' if i % 15 == 0 else\n"
            "        'Fizz' if i % 3 == 0 else\n"
            "        'Buzz' if i % 5 == 0 else\n"
            "        str(i)\n"
            "        for i in range(1, n + 1)\n"
            "    ]\n\n"
            "print('\\n'.join(fizzbuzz(100)))",

            # Гамма (одна строка)
            "print('\\n'.join('Fizz'*(i%3==0)+'Buzz'*(i%5==0) or str(i) for i in range(1,101)))",

            # Дельта (словарь)
            "rules = {3: 'Fizz', 5: 'Buzz'}\n"
            "for i in range(1, 101):\n"
            "    out = ''.join(word for div, word in rules.items() if i % div == 0)\n"
            "    print(out or i)"
        ]

        submissions = []
        for team, code in zip(teams, codes):
            sub = Submission.objects.create(
                battle=battle,
                team=team,
                code_snapshot=code,
                language="python"
            )
            submissions.append(sub)

        self.stdout.write("Добавление голосов...")

        # Имитируем голоса: Альфа - 5, Бета - 3, Гамма - 8, Дельта - 2
        votes_config = [
            (submissions[0], 5),
            (submissions[1], 3),
            (submissions[2], 8),
            (submissions[3], 2),
        ]

        for sub, count in votes_config:
            for j in range(count):
                Vote.objects.create(
                    submission=sub,
                    session_key=f"seed-session-{sub.id}-{j}",
                    voter_ip="127.0.0.1",
                    score=1
                )

        self.stdout.write(self.style.SUCCESS(
            f"✅ Тестовые данные созданы!\n"
            f"Баттл: {battle.title}\n"
            f"Команд: {len(teams)}\n"
            f"Решений: {len(submissions)}\n"
            f"Всего голосов: {sum(c for _, c in votes_config)}"
        ))