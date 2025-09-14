from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create local development users (admin and dev) if they don't exist"

    def handle(self, *args, **options):
        User = get_user_model()

        # Admin user
        admin_email = "admin@local.test"
        admin_username = "admin"
        admin_password = "Admin123!"
        if not User.objects.filter(email=admin_email).exists():
            self.stdout.write("Creating admin user...")
            User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password,
            )
        else:
            self.stdout.write("Admin user already exists — skipping")

        # Dev user
        dev_email = "dev@local.test"
        dev_username = "devuser"
        dev_password = "devpass123!"
        if not User.objects.filter(email=dev_email).exists():
            self.stdout.write("Creating dev user...")
            User.objects.create_user(
                username=dev_username,
                email=dev_email,
                password=dev_password,
            )
        else:
            self.stdout.write("Dev user already exists — skipping")

        self.stdout.write(self.style.SUCCESS("Dev users ensured: admin@local.test / Admin123! | dev@local.test / devpass123!"))

