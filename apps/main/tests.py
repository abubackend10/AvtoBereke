from io import BytesIO
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from PIL import Image

from .models import Car
from .images import MAX_IMAGE_SIZE, optimize_image_upload
from .views import cars


class DevelopmentErrorPageTests(TestCase):
    def test_admin_is_available_at_standard_path(self):
        response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 302)

    def test_unknown_url_shows_custom_404_even_with_debug_enabled(self):
        with override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False):
            response = self.client.get("/ru/does-not-exist/")

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Такой страницы нет", status_code=404)

    def test_missing_car_shows_custom_404_even_with_debug_enabled(self):
        middleware = [*settings.MIDDLEWARE, "core.middleware.Development404Middleware"]
        with override_settings(
            DEBUG=True,
            SECURE_SSL_REDIRECT=False,
            MIDDLEWARE=middleware,
        ):
            response = self.client.get("/ru/cars/does-not-exist/")

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Такой страницы нет", status_code=404)


class EnsureSuperuserTests(TestCase):
    @patch.dict(
        os.environ,
        {
            "DJANGO_SUPERUSER_USERNAME": "deployment-admin",
            "DJANGO_SUPERUSER_EMAIL": "admin@example.com",
            "DJANGO_SUPERUSER_PASSWORD": "A-long-unique-deployment-password-593!",
        },
    )
    def test_creates_superuser_and_is_idempotent(self):
        call_command("ensure_superuser", verbosity=0)
        call_command("ensure_superuser", verbosity=0)

        user = get_user_model().objects.get(username="deployment-admin")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("A-long-unique-deployment-password-593!"))


class ImageOptimizationTests(SimpleTestCase):
    def test_large_opaque_png_is_resized_and_compressed_as_jpeg(self):
        source = BytesIO()
        Image.effect_noise((2400, 1200), 100).convert("RGB").save(source, format="PNG")
        upload = SimpleUploadedFile("car.png", source.getvalue(), content_type="image/png")
        name, optimized = optimize_image_upload(upload.name, upload)

        self.assertTrue(name.endswith(".jpg"))
        with Image.open(optimized) as image:
            self.assertEqual(image.format, "JPEG")
            self.assertLessEqual(image.width, MAX_IMAGE_SIZE[0])
            self.assertLessEqual(image.height, MAX_IMAGE_SIZE[1])


class CarImageUploadTests(TestCase):
    def test_car_save_stores_optimized_photo(self):
        source = BytesIO()
        Image.effect_noise((2400, 1200), 100).convert("RGB").save(source, format="PNG")
        upload = SimpleUploadedFile("car.png", source.getvalue(), content_type="image/png")

        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                car = Car(
                    name="Camry",
                    year=2020,
                    price=10000,
                    mileage="50000 km",
                    engine="2.0 л",
                    color="Black",
                    image=upload,
                )
                car.save()

                self.assertTrue(car.image.name.endswith(".jpg"))
                with Image.open(car.image.path) as optimized:
                    self.assertEqual(optimized.format, "JPEG")
                    self.assertLessEqual(optimized.width, MAX_IMAGE_SIZE[0])

    def test_deleting_car_removes_its_images_from_storage(self):
        source = BytesIO()
        Image.new("RGB", (64, 64), "blue").save(source, format="JPEG")
        image_content = source.getvalue()

        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                car = Car(
                    name="Camry",
                    year=2020,
                    price=10000,
                    mileage="50000 km",
                    engine="2.0 л",
                    color="Black",
                    image=SimpleUploadedFile("main.jpg", image_content),
                )
                car.save()
                gallery_image = car.gallery.create(
                    image=SimpleUploadedFile("gallery.jpg", image_content)
                )
                stored_paths = [car.image.path, gallery_image.image.path]

                with self.captureOnCommitCallbacks(execute=True):
                    car.delete()

                self.assertTrue(all(not Path(path).exists() for path in stored_paths))

    def test_deleting_car_keeps_image_still_used_by_another_car(self):
        source = BytesIO()
        Image.new("RGB", (64, 64), "blue").save(source, format="JPEG")
        upload = SimpleUploadedFile("shared.jpg", source.getvalue())

        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                first_car = Car(
                    name="Camry",
                    year=2020,
                    price=10000,
                    mileage="50000 km",
                    engine="2.0 л",
                    color="Black",
                    image=upload,
                )
                first_car.save()
                second_car = Car(
                    name="Corolla",
                    year=2021,
                    price=12000,
                    mileage="30000 km",
                    engine="1.8 л",
                    color="White",
                    image=first_car.image.name,
                )
                second_car.save()
                image_path = first_car.image.path

                with self.captureOnCommitCallbacks(execute=True):
                    first_car.delete()
                self.assertTrue(Path(image_path).exists())

                with self.captureOnCommitCallbacks(execute=True):
                    second_car.delete()
                self.assertFalse(Path(image_path).exists())


class CarsPaginationTests(TestCase):
    def setUp(self):
        Car.objects.bulk_create([
            Car(
                name=f"Camry {index}",
                slug=f"camry-{index}",
                year=2020,
                price=10000,
                mileage="50000 km",
                engine="2.0 л",
                color="Черный",
            )
            for index in range(13)
        ])
        self.factory = RequestFactory()

    @patch("apps.main.views.render")
    def test_catalog_paginates_and_preserves_filters(self, render_mock):
        request = self.factory.get("/cars/", {"model": "Camry", "page": "2"})

        cars(request)

        context = render_mock.call_args.args[2]
        self.assertEqual(context["page_obj"].paginator.count, 13)
        self.assertEqual(context["page_obj"].number, 2)
        self.assertEqual(len(context["cars"]), 1)
        self.assertEqual(context["query_params"].urlencode(), "model=Camry")