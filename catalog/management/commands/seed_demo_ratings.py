import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from catalog.models import MediaItem, Rating


class Command(BaseCommand):
    help = "Create demo users and seed ratings/comments for random media items."

    def handle(self, *args, **options):
        User = get_user_model()
        media_items = list(MediaItem.objects.filter(is_published=True))

        if not media_items:
            self.stdout.write(self.style.ERROR("No published media items found to rate."))
            return

        usernames = [
            "sakura_fox",
            "midnight_owl",
            "pixel_wave",
            "movie_buff",
            "anime_leaf",
        ]
        comments = {
            "low": [
                "Ледь додивився, не зайшло.",
                "Сильно розчарований, більше не хочу дивитись.",
                "Сюжет нудний, довго йде до чогось.",
                "Гра акторів слабка, історія не чіпляє.",
                "Після середини хотілось вимкнути.",
            ],
            "mid": [
                "Непогано, але без вау-ефекту.",
                "Місцями цікаво, місцями ні.",
                "Є сильні сцени, але загалом посередньо.",
                "Раз подивитись можна, вдруге навряд.",
                "Сюжет нормальний, але фінал підкачав.",
            ],
            "high": [
                "Класний сюжет, дивився із задоволенням.",
                "Музика топ, візуал теж на рівні.",
                "Дивився на одному диханні.",
                "Хороший настрій після перегляду.",
                "Поки що найкраще, що бачив за рік.",
            ],
        }

        total_created = 0
        for idx, username in enumerate(usernames, start=1):
            email = f"{username}@example.com"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                    "is_active": True,
                },
            )
            if created:
                user.set_password("demo12345")
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user {username} (password: demo12345)"))
            else:
                self.stdout.write(f"Using existing user {username}")

            sample_count = min(10, len(media_items))
            items_sample = random.sample(media_items, sample_count)
            for item in items_sample:
                score = random.randint(1, 10)
                if score <= 3:
                    pool = comments["low"]
                elif score <= 7:
                    pool = comments["mid"]
                else:
                    pool = comments["high"]
                comment = random.choice(pool)
                rating, _ = Rating.objects.update_or_create(
                    user=user,
                    media_item=item,
                    defaults={
                        "score": score,
                        "comment": comment,
                        "created_at": timezone.now(),
                    },
                )
                total_created += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded ratings complete. Total ratings set: {total_created}"))
