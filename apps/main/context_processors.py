from .models import SiteSettings, HeroSection, StatisticsItem

def site_settings(request):
    settings_obj, created = SiteSettings.objects.get_or_create(pk=1)
    
    return {
        'site_settings': settings_obj,
        'hero_section': HeroSection.load(),
        'statistics_items': StatisticsItem.objects.all(),
    }