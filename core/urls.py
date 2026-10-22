from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView
from apps.main.views import page_not_found


urlpatterns = [
    path('', include('apps.main.urls')),
    path(settings.ADMIN_URL, admin.site.urls),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admin/', RedirectView.as_view(url='/admin/', query_string=True)),
    path('', include('apps.main.urls')),
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    path('<path:unmatched_path>', page_not_found),
]
