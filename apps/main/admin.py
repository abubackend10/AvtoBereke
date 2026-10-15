from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import (
    SiteSettings, 
    HeroSection, 
    StatisticsItem,
    Brand,
    BodyType,
    GearboxType,
    FuelType,
    DriveType,
    CarImage,
    CarFeature,
    Car
)

@admin.register(SiteSettings)
class SiteSettingsAdmin(TranslationAdmin):
    list_display = ('title', 'phone_display', 'address')

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HeroSection)
class HeroSectionAdmin(TranslationAdmin):
    list_display = ('title', 'description')

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StatisticsItem)
class StatisticsItemAdmin(TranslationAdmin):
    list_display = ('value', 'title', 'icon_class', 'order')
    list_editable = ('order',)


# ==========================================
# АДМИНКА ДЛЯ ДИНАМИЧЕСКИХ СПРАВОЧНИКОВ
# ==========================================

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(BodyType)
class BodyTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(GearboxType)
class GearboxTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(FuelType)
class FuelTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(DriveType)
class DriveTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# ==========================================
# НАСТРОЙКА АДМИНКИ АВТОМОБИЛЕЙ
# ==========================================

class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 3  

class CarFeatureInline(admin.TabularInline):
    model = CarFeature
    extra = 5  # Сразу покажет 5 пустых строк для ввода опций

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'name', 'year', 'price', 'body', 'gearbox', 'fuel', 'is_recommended', 'created_at')
    list_filter = ('is_recommended', 'brand', 'body', 'gearbox', 'fuel', 'drive', 'year')
    search_fields = ('name', 'description')
    readonly_fields = ('slug',)
    inlines = [CarImageInline, CarFeatureInline]
    
    # Группировка полей в форме редактирования для удобства
    fieldsets = (
        ('Основная информация', {
            'fields': ('brand', 'name', 'slug', 'year', 'price', 'image', 'is_recommended')
        }),
        ('Контакты владельца', {
            'fields': ('owner_phone', 'owner_whatsapp')
        }),
        ('Характеристики', {
            'fields': ('mileage', 'engine', 'body', 'gearbox', 'fuel', 'drive', 'color', 'steering', 'customs', 'condition')
        }),
        ('Медиа и описание', {
            'fields': ('instagram_reel_url', 'description')
        }),
    )