# Django imports
from django.conf.urls import url

# Locale impors
from .views import login_view, logout_view, home_view


urlpatterns = [
    url(r'^login/$', login_view, name='login'),
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^home/$', home_view, name='home'),
]
