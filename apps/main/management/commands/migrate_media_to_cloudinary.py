from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.files.storage import storages
from django.core.management.base import BaseCommand, CommandError

from apps.main.images import optimize_image_upload
from apps.main.models import Car, CarImage, SiteSettings


IMAGE_FIELDS = (
    (SiteSettings, "logo"),
    (Car, "image"),
    (CarImage, "image"),
)


class Command(BaseCommand):
    help = "Copy existing local site and car images to Cloudinary."

    def handle(self, *args, **options):
        storage = storages["default"]
        if storage.__class__.__module__ != "cloudinary_storage.storage":
            raise CommandError("Set CLOUDINARY_URL before running this command.")

        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.is_dir():
            raise CommandError(f"Media directory does not exist: {media_root}")

        uploaded = 0
        already_present = 0
        for model, field_name in IMAGE_FIELDS:
            for instance in model.objects.all().iterator():
                image_field = getattr(instance, field_name)
                if not image_field:
                    continue

                name = image_field.name
                local_path = media_root.joinpath(*Path(name).parts)
                if storage.exists(name):
                    already_present += 1
                    continue
                if not local_path.is_file():
                    raise CommandError(f"Missing local image: {local_path}")

                with local_path.open("rb") as source:
                    optimized_name, optimized_file = optimize_image_upload(
                        name, File(source, name=local_path.name)
                    )
                    stored_name = storage.save(optimized_name, optimized_file)

                if stored_name != name:
                    setattr(instance, field_name, stored_name)
                    instance.save(update_fields=[field_name])
                uploaded += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Cloudinary media migration complete: {uploaded} uploaded, "
                f"{already_present} already present. Local originals were kept."
            )
        )
