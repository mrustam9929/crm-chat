from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.models import Group
from django.urls import include, path, re_path

from api.v1.docs.swagger_config import lms_scheme

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('api/', include('api.urls')),
]
# SWAGGER
urlpatterns += [
    re_path(
        r"^api/v1/docs/$", lms_scheme.with_ui('swagger', cache_timeout=0), name='cmo-schema-swagger',
    ),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.unregister(Group)
admin.site.site_header = 'Админ панель'
admin.site.site_title = 'Админ панель'
admin.site.index_title = 'Админ панель'
