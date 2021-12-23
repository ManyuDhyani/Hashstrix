from django.db import models

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        (1, 'Like'),
        (2, 'Comment'),
        (3, 'Follow'),
        (4, 'Reply')
    )
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='notification_post', blank=True, null=True)
    sender = models.ForeignKey('blog.Author', on_delete=models.CASCADE, related_name='notification_from_user')
    receiver = models.ForeignKey('blog.Author', on_delete=models.CASCADE, related_name='notification_to_user')
    notification_type = models.IntegerField(choices=NOTIFICATION_TYPES)
    text_preview = models.CharField(max_length=50, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)
    
    def __str__(self):
        return 'Sender {} to Receiver {} -> Action {}'.format(self.sender.user.username, self.receiver.user.username, self.notification_type)

