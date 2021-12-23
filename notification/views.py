from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Notification
from blog.models import Author

def get_author(user):
    author = Author.objects.filter(user=user)
    if author.exists():
        return author[0]
    return None

@login_required(login_url='/accounts/login/')
def ShowNotification(request):
    user = request.user
    author = get_author(user)
    notifications = Notification.objects.filter(receiver=author).order_by('-date')
    Notification.objects.filter(receiver=author, is_seen=False).update(is_seen=True)

    paginator = Paginator(notifications, 10)
    page_request_variable = 'page'
    page = request.GET.get(page_request_variable)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'notifications': paginated_queryset
    }
    return render(request, 'notification.html', context)

@login_required(login_url='/accounts/login/')
def DeleteNotification(request, notification_id):
    user = request.user
    author = get_author(user)
    Notification.objects.filter(id=notification_id, receiver=author).delete()
    return redirect('show-notifications')

def CountNotifications(request):
    count_notifications = None
    if request.user.is_authenticated:
        user = request.user
        author = get_author(user)
        count_notifications = Notification.objects.filter(receiver=author, is_seen=False).count()
    return {'count_notifications': count_notifications}