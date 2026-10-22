from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Car, CarImage, SiteSettings


@receiver(post_delete, sender=Car)
@receiver(post_delete, sender=CarImage)
def delete_unreferenced_car_image(sender, instance, using, **kwargs):
    image = instance.image
    if not image:
        return

    image_name = image.name
    storage = image.storage

    def delete_if_unreferenced():
        image_fields = (
            (SiteSettings, "logo"),
            (Car, "image"),
            (CarImage, "image"),
        )
        for model, field_name in image_fields:
            if model.objects.using(using).filter(**{field_name: image_name}).exists():
                return
        storage.delete(image_name)

    transaction.on_commit(delete_if_unreferenced, using=using)
