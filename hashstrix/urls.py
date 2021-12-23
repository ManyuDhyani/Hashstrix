from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from ckeditor_uploader import views

urlpatterns = [
    path('hashstrixblogs/admin/', admin.site.urls),
    path('ckeditor/upload/', login_required(views.upload), name='ckeditor_upload'),
    path('ckeditor/browse/', never_cache(login_required(views.browse)), name='ckeditor_browse'),
    path('', include('blog.urls')),
    path('', include('marketing.urls')),
    path('accounts/', include('allauth.urls')),
    path('profile/', include('author.urls', namespace='profile')),
    path('', include('notification.urls'))
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
handler404 = 'blog.views.page_not_found'

admin.site.site_header = "Hashstrix Administration"
admin.site.index_title = "Hashstrix Administrator & Database"