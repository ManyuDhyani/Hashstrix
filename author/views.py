from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import logout

from blog.models import Post, Author
from .models import Followers, Profile
from .forms import ProfilePictureForm, ProfileForm, AcountForm

def get_author(user):
    author = Author.objects.filter(user=user)
    if author.exists():
        return author[0]
    return None

@login_required(login_url='/accounts/login/')
def profile(request):
    logged_in_user = get_author(request.user)
    profile = get_object_or_404(Profile, author=logged_in_user)
    blogs = Post.objects.filter(author=profile.author).order_by('-timestamp')
    followers = Followers.objects.filter(following=logged_in_user)
    total_blogs = len(blogs)
    post_view = sum([x.views for x in blogs])

    paginator = Paginator(blogs, 4)
    page_request_variable = 'page'
    page = request.GET.get(page_request_variable)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'profile': profile,
        'blogs': paginated_queryset,
        'followers': followers,
        'total_blogs': total_blogs,
        'post_view': post_view,
        'page_request_variable': page_request_variable
    }
    return render(request, "profile.html", context)

@login_required(login_url='/accounts/login/')
def visit_profile(request, slug):
    author = get_object_or_404(Author, slug=slug)
    profile = get_object_or_404(Profile, author=author)

    blogs = Post.objects.filter(author=author, status='public').order_by('-timestamp')
    total_blogs = len(blogs)
    post_view = sum([x.views for x in blogs])

    followers = Followers.objects.filter(following=author)
    logged_in_user = get_author(request.user)


    #if already following 1 else 0
    is_following = 1 if Followers.objects.filter(follower=logged_in_user, following=author).exists() else 0

    #for follow
    follow = request.GET.get('follow')
    if follow:
        following = Followers.objects.get_or_create(follower=logged_in_user, following=author)
        if following:
            is_following = 1

    #for unfollow
    unfollow = request.GET.get('unfollow')
    if unfollow:
        try:
            Followers.objects.get(follower=logged_in_user, following=author).delete()
            is_following = 0
        except:
            is_following = 0

    paginator = Paginator(blogs, 4)
    page_request_variable = 'page'
    page = request.GET.get(page_request_variable)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'profile': profile,
        'blogs': paginated_queryset,
        'followers': followers,
        'total_blogs': total_blogs,
        'post_view': post_view,
        'follow_status': is_following,
        'page_request_variable': page_request_variable
    }

    return render(request, "profile.html", context)

@login_required(login_url='/accounts/login/')
def settings(request):
    logged_in_user = request.user
    author = get_author(logged_in_user)
    profile = get_object_or_404(Profile, author__user=logged_in_user)
    profile_picture_form = ProfilePictureForm(request.POST or None, request.FILES or None, instance=author)
    profile_form = ProfileForm(request.POST or None, instance=profile)
    account_form = AcountForm(request.POST or None, instance=logged_in_user)
    password_form = PasswordChangeForm(request.user, request.POST)

    if request.method == "POST":
        if 'profile' in request.POST:
            if 'profile_picture' in request.POST.get('profile'):
                if profile_picture_form.is_valid():
                    profile_picture_form.save()
            elif 'profile_details' in request.POST.get('profile'):
                if profile_form.is_valid():
                    profile_form.instance.author = author
                    bio = profile_form.cleaned_data.get('bio')
                    link1 = profile_form.cleaned_data.get('link1')
                    link2 = profile_form.cleaned_data.get('link2')
                    linkedin = profile_form.cleaned_data.get('linkedin')
                    youtube = profile_form.cleaned_data.get('youtube')
                    location = profile_form.cleaned_data.get('location')
                    profile_form.save()
            return redirect(reverse("profile:settings"))
        elif 'account' in request.POST:
            if account_form.is_valid():
                username = account_form.cleaned_data.get('username')
                first_name = account_form.cleaned_data.get('first_name')
                last_name = account_form.cleaned_data.get('last_name')
                account_form.save()
                return redirect(reverse("profile:settings"))
        elif 'delete' in request.POST:
            User = get_user_model()
            username = request.POST.get('delete')
            try:
                if username == request.user.username:
                    user = get_object_or_404(User, username=username)
                    user.delete()
                    return redirect(reverse("account_signup"))
            except:
                return redirect(reverse("profile:settings"))
        elif 'password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated! Try login with new password')
                logout(request)
                return redirect(reverse("account_login"))
            else:
                messages.error(request, 'Password has not been updated successfully. Please Try again!')
                return redirect(reverse("profile:settings"))
    else:
        password_form = PasswordChangeForm(request.user)

    context = {
        'profile': profile,
        'profile_picture_form': profile_picture_form,
        'form': profile_form,
        'account_form': account_form,
        'password_form': password_form
    }
    return render(request, 'settings.html', context)