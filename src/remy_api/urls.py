from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

from apps.api.admin import admin


favicon_view = RedirectView.as_view(url=f'{settings.MEDIA_URL}favicon_v1.ico')

urlpatterns = [
    re_path(r'^favicon\.ico$', favicon_view),
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.api.urls'), name='api'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += static(settings.MEDIA_URL + 'images',
                          document_root=settings.MEDIA_ROOT + '/images')
