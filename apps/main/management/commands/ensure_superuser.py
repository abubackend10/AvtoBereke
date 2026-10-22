import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the deployment superuser from environment variables if it does not exist."

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "").strip()
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "")
        if not username or not email or not password:
            raise CommandError(
                "Set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, "
                "and DJANGO_SUPERUSER_PASSWORD."
            )

        user_model = get_user_model()
        user_field = user_model.USERNAME_FIELD
        user_lookup = {user_field: username}
        existing_user = user_model.objects.filter(**user_lookup).first()
        if existing_user:
            if not existing_user.is_superuser:
                raise CommandError(
                    f"A non-superuser already exists with {user_field}={username!r}."
                )
            self.stdout.write("Deployment superuser already exists.")
            return

        user = user_model(**user_lookup, email=email)
        try:
            validate_password(password, user=user)
        except ValidationError as error:
            raise CommandError(
                "The deployment superuser password is not strong enough."
            ) from error

        user_model.objects.create_superuser(
            **user_lookup,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS("Deployment superuser created."))
