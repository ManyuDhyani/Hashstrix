from django.urls import path
from .views import (
    profile, visit_profile, settings
)

app_name = 'author'

urlpatterns = [
    path('account/', profile, name='account_login'),
    path('<slug>', visit_profile, name='visit-profile'),
    path('settings/', settings, name='settings'),
    ]