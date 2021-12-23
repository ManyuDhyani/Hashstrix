from django.contrib import admin
from .models import Profile, Followers

from simple_history.admin import SimpleHistoryAdmin

class ProfileHistoryAdmin(SimpleHistoryAdmin):
    list_display = ["id", "author"]
    history_list_display = ["author"]
    search_fields = ["author__user__username"]

admin.site.register(Profile, ProfileHistoryAdmin)


admin.site.register(Followers)