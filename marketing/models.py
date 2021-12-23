from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

class Signup(models.Model):
    email = models.EmailField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = "Newsletter"

class TermsCondition(models.Model):
    content = RichTextUploadingField()

    class Meta:
        verbose_name_plural = "Terms & Condition"

class CommunityGuidelines(models.Model):
    content = RichTextUploadingField()

    class Meta:
        verbose_name_plural = "Community Guidelines"

class PrivacyPolicy(models.Model):
    content = RichTextUploadingField()

    class Meta:
        verbose_name_plural = "Privacy Policy"

class HowItWorks(models.Model):
    content = RichTextUploadingField()

    class Meta:
        verbose_name_plural = "How It Works"

class Quotes(models.Model):
    line1 = models.CharField(max_length=100)
    line2 = models.CharField(max_length=100, null=True, blank=True)
    line3 = models.CharField(max_length=100, null=True, blank=True)
    line4 = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Home Quotes"
