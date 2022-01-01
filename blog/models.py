from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from .utils import unique_slug_generator_title
from taggit.managers import TaggableManager
from django.db.models.signals import pre_save, post_save, post_delete
from .utilsAuthor import unique_slug_generator
from simple_history.models import HistoricalRecords

from notification.models import Notification

User = get_user_model()

@receiver(post_save, sender=User)
def create_author(sender, instance, created, **kwargs):
    if created:
        Author.objects.create(user=instance)

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profilePictures/%Y/%m/%d/', default="img/profile2.png", null=True, blank=True)
    slug = models.SlugField(max_length=250, null=True, blank=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('profile:visit-profile', kwargs={
            'slug': self.slug
        })

def slug_author_generator(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(slug_author_generator, sender=Author)

class Category(models.Model):
    title = models.CharField(max_length=30)
    slug = models.SlugField(max_length=30, null=True, blank=True)
    
    def __str__(self):
        return self.title
        
def slug_generator(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator_title(instance)

pre_save.connect(slug_generator, sender=Category)


STATUS_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private')
    )

class PostChangeUser(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

class Post(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=250, null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)#Remove null blank
    date = models.DateField(auto_now_add=True)#Remove null blank
    content = RichTextUploadingField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    thumbnail = models.ImageField(upload_to='thumbnails/%Y/%m/%d/')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)#remove null=True in production
    previous_post = models.ForeignKey('self', related_name='previous', on_delete=models.SET_NULL, blank=True, null=True)
    next_post = models.ForeignKey('self', related_name='next', on_delete=models.SET_NULL, blank=True, null=True)
    tags = TaggableManager()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='public')
    liked = models.ManyToManyField(Author, blank=True, related_name='likes')
    changed_by = models.ForeignKey(PostChangeUser, on_delete=models.CASCADE, null=True, blank=True)#remove null=True & blank in production
    history = HistoricalRecords()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={
            'slug': self.slug
        })

    def get_update_url(self):
        return reverse('post-update', kwargs={
            'slug': self.slug
        })

    def get_delete_url(self):
        return reverse('post-delete', kwargs={
            'slug': self.slug
        })

    @property
    def get_comments(self):
        return self.comments.all().order_by('-timestamp')


    @property
    def views(self):
        return PostView.objects.filter(post=self).count()


    @property
    def comment_count(self):
        return Comment.objects.filter(post=self).count()

    @property
    def num_likes(self):
        return self.liked.all().count()

pre_save.connect(slug_generator, sender=Post)

class CommentManager(models.Manager):
    def all(self):
        qs = super(CommentManager, self).filter(parent=None)
        return qs


class Comment(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    content = models.TextField()

    objects = CommentManager()

    def __str__(self):
        return 'Comment by {} on {}-{}'.format(self.author, self.post, self.id)

    def children(self):
        return Comment.objects.filter(parent=self).order_by('timestamp')

    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True

    def user_commented_on_post(sender, instance, *args, **kwargs):
        comment = instance
        post = comment.post
        sender = comment.author
        receiver = post.author
        text_preview = comment.content[:50]
        if sender != receiver:
            notify = Notification(post=post, sender=sender, receiver=receiver, text_preview=text_preview, notification_type=2)
            notify.save()

    def user_deleted_comment_on_post(sender, instance, *args, **kwargs):
        comment = instance
        post = comment.post
        sender = comment.author

        notify = Notification.objects.filter(post=post, sender=sender, notification_type=2)
        notify.delete()

    #User Reply
    def user_replied_on_comment(sender, instance, *args, **kwargs):
        comment = instance
        post = comment.post
        sender = comment.author
        text_preview = comment.content[:50]
        receiver = None
        if comment.parent:
            receiver = comment.parent.author

        if receiver and sender != receiver:
            notify = Notification(post=post, sender=sender, receiver=receiver, text_preview=text_preview, notification_type=4)
            notify.save()

    def user_deleted_reply_on_comment(sender, instance, *args, **kwargs):
        comment = instance
        post = comment.post
        sender = comment.author
        text_preview = comment.content[:50]
        notify = Notification.objects.filter(post=post, sender=sender, text_preview=text_preview, notification_type=4)
        notify.delete()


#Signals for Comment Notification
post_save.connect(Comment.user_commented_on_post, sender=Comment)
post_delete.connect(Comment.user_deleted_comment_on_post, sender=Comment)

#Signals for Comment Reply Notification
post_save.connect(Comment.user_replied_on_comment, sender=Comment)
post_delete.connect(Comment.user_deleted_reply_on_comment, sender=Comment)

class PostView(models.Model):
    ip = models.CharField(max_length=50)
    post = models.ForeignKey(Post,  on_delete=models.CASCADE)

    def __str__(self):
        return 'Viewed by {} -> post {}'.format(self.ip, self.post)
        
class Like(models.Model):
    user = models.ForeignKey(Author, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.CharField(max_length=8)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}-{self.post}-{self.value}"

    def user_liked_post(sender, instance, *args, **kwargs):
        like = instance
        post = like.post
        sender = like.user
        receiver = post.author

        if sender != receiver:
            notify = Notification(post=post, sender=sender, receiver=receiver, notification_type=1)
            notify.save()

    def user_unliked_post(sender, instance, *args, **kwargs):
        like = instance
        post = like.post
        sender = like.user

        notify = Notification.objects.filter(post=post, sender=sender, notification_type=1)
        notify.delete()

#Signals for Likes Notification
post_save.connect(Like.user_liked_post, sender=Like)
post_delete.connect(Like.user_unliked_post, sender=Like)