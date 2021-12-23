from django.urls import path
from .views import post_share, how_it_works, terms_condition, community_guidelines, privacy_policy, plain_text_view

urlpatterns = [
    path('share/<slug>', post_share, name='share'),
    path('how-it-works', how_it_works, name='how-it-works'),
    path('terms-and-condition', terms_condition, name='terms-and-condition'),
    path('community-guidelines', community_guidelines, name='community-guidelines'),
    path('privacy-policy', privacy_policy, name='privacy-policy'),
    path('ads.txt', plain_text_view, name='ads'),
]