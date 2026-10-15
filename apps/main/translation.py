from modeltranslation.translator import register, TranslationOptions, translator
from .models import SiteSettings, HeroSection, StatisticsItem, Car

@register(SiteSettings)
class SiteSettingsTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'address')

@register(HeroSection)
class HeroSectionTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(StatisticsItem)
class StatisticsItemTranslationOptions(TranslationOptions):
    fields = ('title',)

class CarTranslationOptions(TranslationOptions):
    fields = ( 
        'description',
    )

translator.register(Car, CarTranslationOptions)