from django.urls import path
from .views import (
    index, blog, post, search,
    post_create, post_update, post_delete,
    trending, latest, delete_comment, like_unlike_post,
    PostList, PostUpdateDelete, TrendingList, AuthorList, AuthorUpdateDelete, UserList, traveloftindiaBlogs
)

urlpatterns = [
    path('', index, name='home'),
    path('trending/', trending, name='trending'),
    path('latest/', latest, name='latest'),
    path('blogs/', blog, name='blog-list'),
    path('cateogory/<slug:category_slug>/', blog, name='post_list_by_category'),
    path('tag/<slug:tag_slug>/', blog, name='post_list_by_tag'),
    path('search/', search, name='search'),
    path('create/', post_create, name='post-create'),
    path('post/<slug>/', post, name='post-detail'),
    path('post/<slug>/update/', post_update, name='post-update'),
    path('post/<slug>/delete/', post_delete, name='post-delete'),
    path('comment', delete_comment, name='delete-comment'),
    path('liked/', like_unlike_post, name='like-post-view'),
    
    #API URLs
    path('api/blogs/', PostList.as_view()),
    path('api/blog/<int:pk>', PostUpdateDelete.as_view()),
    path('api/trending/', TrendingList.as_view()),
    path('api/authors/', AuthorList.as_view()),
    path('api/author/<int:pk>', AuthorUpdateDelete.as_view()),
    path('api/users/', UserList.as_view()),
    path('api/traveloftindia/', traveloftindiaBlogs.as_view()),
]
