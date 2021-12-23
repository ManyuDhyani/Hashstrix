from django.urls import path
from .views import ShowNotification, DeleteNotification

urlpatterns = [
    path('notifications', ShowNotification, name='show-notifications'),
    path('<notification_id>/delete', DeleteNotification, name='delete-notification')
]