# Django imports
from django.conf.urls import include, url, patterns
from django.conf import settings
from django.contrib import admin
# from django.views.generic import RedirectView

# locale imports
# from . import main

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('main.urls', namespace='main')),
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
    except:
        pass
