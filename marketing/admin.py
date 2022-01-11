from django.contrib import admin
from .models import *

admin.site.register(Signup)

admin.site.register(Quotes)

admin.site.register(TermsCondition)
admin.site.register(CommunityGuidelines)
admin.site.register(PrivacyPolicy)
admin.site.register(HowItWorks)
admin.site.register(Announcement)