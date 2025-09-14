import os
import random
import uuid
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from birds.models import Bird, Comment, Reply, Seed


SPECIES = [
    "American Robin",
    "House Sparrow",
    "Northern Cardinal",
    "Blue Jay",
    "European Starling",
    "Mourning Dove",
    "Black-capped Chickadee",
    "Red-tailed Hawk",
    "Mallard",
    "Great Blue Heron",
    "Peregrine Falcon",
    "Barn Swallow",
]

LOCATIONS = [
    ("Central Park, New York, USA", 40.7812, -73.9665),
    ("Golden Gate Park, San Francisco, USA", 37.7694, -122.4862),
    ("Lincoln Park, Chicago, USA", 41.9214, -87.6513),
    ("Hyde Park, London, UK", 51.5073, -0.1657),
    ("Ibirapuera Park, São Paulo, Brazil", -23.5874, -46.6576),
    ("Yoyogi Park, Tokyo, Japan", 35.6728, 139.6949),
    ("Royal Botanic Garden, Sydney, Australia", -33.8642, 151.2166),
    ("Kirstenbosch Garden, Cape Town, South Africa", -33.9881, 18.4320),
]


class Command(BaseCommand):
    help = "Seed believable dummy data with random bird pictures and comments"

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=16, help="How many birds to create total (or per user with --per-user)")
        parser.add_argument("--for-users", type=str, default="", help="Comma-separated list of user emails or usernames to seed for")
        parser.add_argument("--per-user", action="store_true", help="Interpret --count as per-user count rather than total")

    def handle(self, *args, **options):
        count = options["count"]
        User = get_user_model()

        # Resolve target users
        targets = []
        if options["for_users"]:
            tokens = [t.strip() for t in options["for_users"].split(",") if t.strip()]
            for token in tokens:
                u = User.objects.filter(email__iexact=token).first() or User.objects.filter(username__iexact=token).first()
                if u:
                    targets.append(u)
                else:
                    self.stdout.write(self.style.WARNING(f"User not found: {token}"))
        else:
            # default to dev and admin if present, otherwise any superuser, otherwise create a seed user
            for token in ["dev@local.test", "admin@local.test"]:
                u = User.objects.filter(email__iexact=token).first()
                if u:
                    targets.append(u)
            if not targets:
                u = User.objects.filter(is_superuser=True).first()
                if u:
                    targets.append(u)
            if not targets:
                u = User.objects.create_user(
                    username="seeduser",
                    email="seeduser@local.test",
                    password="seedpass123!",
                )
                targets.append(u)
                self.stdout.write("Created seed user seeduser@local.test / seedpass123!")

        images_dir = Path("media/test_birds")
        if not images_dir.exists():
            self.stdout.write(self.style.WARNING("No local test images found in media/test_birds; seeding without images."))
        image_paths = [p for p in images_dir.glob("*.*") if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".jfif"}]
        if not image_paths:
            self.stdout.write(self.style.WARNING("No matching image files in media/test_birds"))

        total_created = 0
        per_user_count = count if options["per_user"] or len(targets) == 1 else max(1, count // max(1, len(targets)))
        for user in targets:
            created = 0
            for _ in range(per_user_count):
                species = random.choice(SPECIES)
                location, lat, lng = random.choice(LOCATIONS)

                bird = Bird(
                    species=species,
                    location=location,
                    latitude=lat + random.uniform(-0.01, 0.01),
                    longitude=lng + random.uniform(-0.01, 0.01),
                    photographer=user,
                    photographer_comment=random.choice([
                        "Spotted near a pond just after sunrise.",
                        "Very curious bird, didn’t mind me getting close.",
                        "Took this during a weekend walk in the park.",
                        "Perched on a branch calling loudly.",
                        "I’ve never seen this species here before!",
                    ]),
                )

                if image_paths:
                    img_path = random.choice(image_paths)
                    with open(img_path, "rb") as f:
                        # Give it a unique filename to avoid clashes
                        ext = img_path.suffix.lower().lstrip('.') or 'jpg'
                        filename = f"seed_{uuid.uuid4().hex}.{ext}"
                        bird.picture.save(filename, File(f), save=False)

                bird.save()
                created += 1
                total_created += 1

                # Add a few comments and seeds
                if random.random() < 0.8:
                    Comment.objects.create(
                        bird=bird,
                        comment_creator=user,
                        comment=random.choice([
                            "Lovely capture!",
                            "Amazing colors!",
                            "I think I saw one just like this.",
                            "Great shot, thanks for sharing!",
                        ]),
                        comment_approved=True,
                    )
                if random.random() < 0.7:
                    Seed.objects.create(bird=bird, seeder=user, seeded=True)

            self.stdout.write(self.style.SUCCESS(f"Created {created} birds for {user.username}"))
        self.stdout.write(self.style.SUCCESS(f"Total created: {total_created}"))
