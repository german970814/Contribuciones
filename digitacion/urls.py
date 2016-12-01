# Django imports
from django.conf.urls import include, url
from django.contrib import admin

# locale imports
# from . import main


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('main.urls', namespace='main')),
]
