from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from blog.models import Author, PostView
from simple_history.models import HistoricalRecords

from notification.models import Notification

User = get_user_model()

@receiver(post_save, sender=Author)
def create_author(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(author=instance)

class ProfileChangeUser(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

class Profile(models.Model):
    author = models.ForeignKey("blog.Author", on_delete=models.CASCADE)
    bio = models.CharField(max_length=100, null=True, blank=True)
    link1 = models.URLField(max_length=100, null=True, blank=True)
    link2 = models.URLField(max_length=100, null=True, blank=True)
    linkedin = models.URLField(max_length=100, null=True, blank=True)
    youtube = models.URLField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    changed_by = models.ForeignKey(ProfileChangeUser, on_delete=models.CASCADE, null=True, blank=True)#remove null=True & blank in production
    history = HistoricalRecords()

    def __str__(self):
        return self.author.user.username


class Followers(models.Model):
    follower = models.ForeignKey('blog.Author', related_name='follower', on_delete=models.CASCADE)
    following = models.ForeignKey('blog.Author', related_name='following', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Followers"


    def __str__(self):
        return '{} started following {}'.format(self.follower.user.username, self.following.user.username)

    def user_followed(sender, instance, *args, **kwargs):
        follow = instance
        sender = follow.follower
        receiver = follow.following

        notify = Notification(sender=sender, receiver=receiver, notification_type=3)
        notify.save()

    def user_unfollowed(sender, instance, *args, **kwargs):
        follow = instance
        sender = follow.follower
        receiver = follow.following

        notify = Notification.objects.filter(sender=sender, receiver=receiver, notification_type=3)
        notify.delete()

#Signals for Followers Notification
post_save.connect(Followers.user_followed, sender=Followers)
post_delete.connect(Followers.user_unfollowed, sender=Followers)