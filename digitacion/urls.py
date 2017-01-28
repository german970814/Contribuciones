# Django imports
from django.conf.urls import include, url, patterns
from django.conf import settings
from django.contrib import admin
# from django.views.generic import RedirectView

# locale imports
# from . import main
from script import importar_sobres_excel_view

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('main.urls', namespace='main')),
    url(r'^import_data/excel/', importar_sobres_excel_view, name='importar_sobres_excel'),
    # url(r'^/$', RedirectView.as_view(url="/login/")),
]

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, }),
    )

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass
