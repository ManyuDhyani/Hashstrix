from django.contrib import admin
from .models import Author, Category, Post, Comment, PostView, Like

from simple_history.admin import SimpleHistoryAdmin

admin.site.register(Author)

admin.site.register(Category)

class PostHistoryAdmin(SimpleHistoryAdmin):
    list_display = ["id", "author", 'title', 'timestamp', 'updated']
    #history_list_display = ["author"]
    list_display_links = ['title', 'updated']
    search_fields = ['name', 'user__username']
    search_fields = ['title', "author__user__username"]
    list_filter = ['category']
    save_on_top = True
admin.site.register(Post, PostHistoryAdmin)

admin.site.register(Comment)

admin.site.register(PostView)

admin.site.register(Like)