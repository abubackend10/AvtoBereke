from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class SiteSettings(SingletonModel):
    title = models.CharField(
        max_length=150,
        verbose_name="Название сайта (Title)"
    )
    logo = models.ImageField(
        upload_to='site/', 
        blank=True, null=True, 
        verbose_name="Логотип сайта"
    )
    description = CKEditor5Field(
        verbose_name="Описание / Слоган (в футере)"
    )
    whatsapp_num = models.CharField(
        max_length=50,  
        verbose_name="Номер WhatsApp / Телефон (без плюса)"
    )
    phone_display = models.CharField(
        max_length=50, 
        verbose_name="Телефон для отображения"
    )
    address = models.CharField(
        max_length=255, 
        verbose_name="Адрес салона"
    )
    map_iframe = models.TextField(blank=True, null=True, verbose_name='Ссылка от iframe (Google Maps)')
    
    instagram = models.CharField(blank=True, null=True, verbose_name="Instagram (Ник)")
    telegram = models.CharField(blank=True, null=True, verbose_name="Telegram (Ник)")
    tiktok = models.CharField(blank=True, null=True, verbose_name="TikTok (Ник)")
    youtube = models.CharField(blank=True, null=True, verbose_name="YouTube (Название канала)")

    class Meta:
        verbose_name = "01) Настройки сайта"
        verbose_name_plural = "01) Настройки сайта"

    def __str__(self):
        return "Глобальные настройки сайта"


class HeroSection(SingletonModel):
    title = models.CharField(max_length=255, verbose_name="Главный заголовок")
    description = CKEditor5Field(verbose_name="Описание / Подзаголовок")

    class Meta:
        verbose_name = "02) Главный блок (Hero)"
        verbose_name_plural = "02) Главный блок (Hero)"

    def __str__(self):
        return "Главный блок сайта"


class StatisticsItem(models.Model):
    value = models.CharField(max_length=50, verbose_name="Значение", help_text="Например: 2 000+, 1 800+, 8, 100%")
    title = models.CharField(max_length=255, verbose_name="Подпись")
    icon_class = models.CharField(
        max_length=100, 
        default="fa-solid fa-car", 
        verbose_name="Класс иконки FontAwesome", 
        help_text="Например: fa-solid fa-car, fa-solid fa-face-smile, fa-solid fa-calendar-days, fa-solid fa-shield-halved"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")

    class Meta:
        ordering = ['order']
        verbose_name = "03) Элемент статистики"
        verbose_name_plural = "03) Элементы статистики"

    def __str__(self):
        return f"{self.value} — {self.title}"


# ==========================================
# ДИНАМИЧЕСКИЕ СПРАВОЧНИКИ ДЛЯ АДМИНКИ
# ==========================================

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Марка автомобиля")

    class Meta:
        verbose_name = "Марка автомобиля"
        verbose_name_plural = "Марки автомобилей"
        ordering = ['name']

    def __str__(self):
        return self.name


class BodyType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Тип кузова")

    class Meta:
        verbose_name = "Тип кузова"
        verbose_name_plural = "Типы кузова"
        ordering = ['name']

    def __str__(self):
        return self.name


class GearboxType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Коробка передач")

    class Meta:
        verbose_name = "Коробка передач"
        verbose_name_plural = "Коробки передач"
        ordering = ['name']

    def __str__(self):
        return self.name


class FuelType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Тип топлива / двигателя")

    class Meta:
        verbose_name = "Тип топлива"
        verbose_name_plural = "Типы топлива"
        ordering = ['name']

    def __str__(self):
        return self.name


class DriveType(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Тип привода")

    class Meta:
        verbose_name = "Привод"
        verbose_name_plural = "Приводы"
        ordering = ['name']

    def __str__(self):
        return self.name


# ==========================================
# ОСНОВНАЯ МОДЕЛЬ АВТОМОБИЛЯ
# ==========================================

class Car(models.Model):
    
    STEERING_CHOICES = [
        ('Слева', 'Слева'),
        ('Справа', 'Справа'),
    ]

    CUSTOMS_CHOICES = [
        ('Растаможен', 'Растаможен'),
        ('Не растаможен', 'Не растаможен'),
        ('В пути / На заказ', 'В пути / На заказ'),
    ]

    CONDITION_CHOICES = [
        ('Идеальное', 'Идеальное / Отличное'),
        ('Хорошее', 'Хорошее'),
        ('Требует ремонта', 'Требует ремонта'),
    ]

    # --- Основные поля ---
    brand = models.ForeignKey(
        Brand, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Марка"
    )
    name = models.CharField(max_length=200, verbose_name="Модель / Название")
    slug = models.SlugField(unique=True, blank=True, verbose_name="URL (slug)")
    year = models.PositiveIntegerField(verbose_name="Год выпуска")
    price = models.PositiveIntegerField(verbose_name="Цена ($)")
    image = models.ImageField(upload_to='cars/', blank=True, null=True, verbose_name="Главное фото")
    
    owner_phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name="Телефон владельца",
        help_text="Прямой номер для звонка (например, 0555123456 или +996555123456)"
    )
    owner_whatsapp = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name="WhatsApp владельца",
        help_text="Номер WhatsApp владельца (только цифры с кодом страны, например: 996555123456)"
    )

    @property
    def effective_phone(self):
        if self.owner_phone and self.owner_phone.strip():
            return self.owner_phone.strip()
        if self.owner_whatsapp and self.owner_whatsapp.strip():
            return self.owner_whatsapp.strip()
        return None

    @property
    def effective_whatsapp(self):
        raw_num = None
        if self.owner_whatsapp and self.owner_whatsapp.strip():
            raw_num = self.owner_whatsapp.strip()
        elif self.owner_phone and self.owner_phone.strip():
            raw_num = self.owner_phone.strip()

        if raw_num:
            clean = "".join(filter(str.isdigit, raw_num))
            if clean.startswith("0") and len(clean) == 10:
                clean = "996" + clean[1:]
            return clean
        return None
    
    is_recommended = models.BooleanField(default=False, verbose_name="Показывать в рекомендации")
    description = CKEditor5Field(verbose_name="Описание автомобиля", blank=True, null=True)

    # --- Характеристики (динамические связи со справочниками) ---
    mileage = models.CharField(max_length=50, verbose_name="Пробег")
    engine = models.CharField(max_length=100, verbose_name="Двигатель (напр. 2.5 л)")
    
    body = models.ForeignKey(
        BodyType, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Кузов"
    )
    gearbox = models.ForeignKey(
        GearboxType, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Коробка передач"
    )
    fuel = models.ForeignKey(
        FuelType, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Топливо / Двигатель"
    )
    drive = models.ForeignKey(
        DriveType, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Привод"
    )

    color = models.CharField(max_length=50, verbose_name="Цвет")
    
    steering = models.CharField(
        max_length=50, 
        choices=STEERING_CHOICES, 
        default='Слева', 
        verbose_name="Руль"
    )
    customs = models.CharField(
        max_length=100, 
        choices=CUSTOMS_CHOICES, 
        default='Растаможен', 
        verbose_name="Таможня"
    )
    condition = models.CharField(
        max_length=100, 
        choices=CONDITION_CHOICES, 
        default='Идеальное', 
        verbose_name="Состояние"
    )

    # Ссылка на видео в Instagram
    instagram_reel_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на Instagram Reels")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def save(self, *args, **kwargs):
        if not self.slug:
            ru_to_en = {
                'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
                'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
                'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
                'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
                'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
            }
            brand_name = self.brand.name if self.brand else "car"
            raw_string = f"{brand_name}-{self.name}-{self.year}".lower()
            translit_string = "".join([ru_to_en.get(char, char) for char in raw_string])
            
            base_slug = slugify(translit_string)
            slug = base_slug
            counter = 1
            while Car.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
            
        super().save(*args, **kwargs)

    def __str__(self):
        brand_name = self.brand.name if self.brand else ""
        return f"{brand_name} {self.name} ({self.year})"


# Модель для галереи дополнительных фото
class CarImage(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='gallery', verbose_name="Автомобиль")
    image = models.ImageField(upload_to='cars/gallery/', verbose_name="Фото галереи")

    def __str__(self):
        return f"Фото для {self.car.name}"


# Модель для опций комплектации
class CarFeature(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='features', verbose_name="Автомобиль")
    name = models.CharField(max_length=255, verbose_name="Название опции")

    def __str__(self):
        return self.name