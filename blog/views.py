from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When
from datetime import date, timedelta

from .models import Post, Category, Author, PostView, Comment, Like, User
from author.models import Profile, Followers
from marketing.models import Signup
from taggit.models import Tag
from .forms import CommentForm, PostForm
from marketing.models import Quotes


from .serializers import PostSerializer, AuthorSerializer, AuthUserSerializer, TraveloftindiaPostSerializer
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView

#from django.conf import settings
#from django.core.cache.backends.base import DEFAULT_TIMEOUT
#from django.views.decorators.cache import cache_page

#CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


def get_author(user):
    author = Author.objects.filter(user=user)
    if author.exists():
        return author[0]
    return None
 
#API Functions    
class PostList(ListAPIView):
    queryset = Post.objects.filter(status='public').order_by('-timestamp')
    serializer_class = PostSerializer


class PostUpdateDelete(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
class TrendingList(ListAPIView):
    d = date.today() - timedelta(days=60)
    trending = Post.objects.filter(status='public', date__gte=d)
    views = PostView.objects.filter(post__in=[p for p in trending]).values("post").annotate(post_count=Count('post')).order_by('-post_count')
    pk_list = [v['post'] for v in views]
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
    queryset = Post.objects.filter(pk__in=pk_list).order_by(preserved)
    serializer_class = PostSerializer
    
class AuthorList(ListAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    
class AuthorUpdateDelete(RetrieveUpdateDestroyAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

class UserList(ListAPIView):
    queryset = User.objects.all()
    serializer_class = AuthUserSerializer

class traveloftindiaBlogs(ListAPIView):
    queryset = Post.objects.filter(tags__name__in=['traveloft', 'traveloftindia']).order_by('-timestamp').distinct()[:3]
    serializer_class = TraveloftindiaPostSerializer

def AllCategories(request):
    categories = Category.objects.all()
    print(categories)
    return {'categories': categories}

def get_category_count():
    category_count = Post.objects.values('category__title', 'category__slug').annotate(trend_count=Count('category__title')).order_by('-trend_count')[:6]
    return category_count

def page_not_found(request, exception):
    return render(request, '404.html')
    
def index(request):
    quotes = Quotes.objects.first()

    d = date.today() - timedelta(days=30)
    trending = Post.objects.filter(status='public', date__gte=d)
    views = PostView.objects.filter(post__in=[p for p in trending]).values("post").annotate(post_count=Count('post')).order_by('-post_count')
    pk_list = [v['post'] for v in views]
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
    featured_Post = Post.objects.filter(pk__in=pk_list).order_by(preserved)[:3]

    latest_Post = Post.objects.filter(status='public').order_by('-timestamp')[0:3]

    if request.method == "POST":
        email = request.POST["email"]
        new_signup = Signup()
        new_signup.email = email
        new_signup.save()

    context = {
        'featured_list': featured_Post,
        'latest_list': latest_Post,
        'quotes': quotes
    }
    return render(request, 'index.html', context)

def blog(request, category_slug=None, tag_slug=None):
    feed = 'world' if request.GET.get('feed') is None else request.GET.get('feed')
    if feed == 'world':
        article_list = Post.objects.filter(status='public').order_by('-timestamp')
        most_recent = Post.objects.filter(status='public').order_by('-timestamp')[:3]
        category_count_variable = get_category_count()
        tags = Post.objects.filter(status='public').values('tags__name', 'tags__slug').annotate(Count('tags__name')).order_by('-tags__name__count')[:10]


        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            article_list = Post.objects.filter(status='public', category=category).order_by('-timestamp')

        if tag_slug:
            tag_post = get_object_or_404(Tag, slug=tag_slug)
            article_list = article_list.filter(status='public', tags__in=[tag_post]).order_by('-timestamp')

    elif feed == 'following':
        logged_in_author = get_author(request.user)
        following_list = Followers.objects.filter(follower=logged_in_author).values_list('following')
        article_list = Post.objects.filter(author__user__in=[u for u in following_list], status='public').order_by('-timestamp')
        most_recent = Post.objects.filter(author__user__in=[u for u in following_list], status='public').order_by('-timestamp')[:3]
        category_count_variable = get_category_count()
        tags = Post.objects.filter(author__user__in=[u for u in following_list], status='public').values('tags__name', 'tags__slug').annotate(Count('tags__name')).order_by('-tags__name__count')[:10]


        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            article_list = Post.objects.filter(status='public', category=category).order_by('-timestamp')

        if tag_slug:
            tag_post = get_object_or_404(Tag, slug=tag_slug)
            article_list = article_list.filter(status='public', tags__in=[tag_post]).order_by('-timestamp')

    paginator = Paginator(article_list, 8)
    page_request_variable = 'page'
    page = request.GET.get(page_request_variable)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'article_list': paginated_queryset,
        'most_recent': most_recent,
        'category_count': category_count_variable,
        'tags': tags,
        'page_request_variable': page_request_variable
    }
    return render(request, 'blog.html', context)


def search(request):
    blog_list = Post.objects.filter(status='public')
    profile_list = Profile.objects.all()
    query = request.GET.get('search')
    category = request.GET.get('category')
    list = Post.objects.none() if category == 'blog' else Profile.objects.none()

    # flags for list_blog and list_account
    lb = 1
    la = 1

    if query == '':
        return redirect(reverse('blog-list'))
    elif len(query) > 100:
        lb = 0
        la = 0
    elif query and category == 'blog':
        list = blog_list.filter(
            Q(title__icontains=query) |
            Q(overview__icontains=query)
        ).distinct()
        lb = 1 if len(list) != 0 else 0
        la = 0
    elif query and category == 'account':
        list = profile_list.filter(
            Q(author__user__username__istartswith=query)
        )
        la = 1 if len(list) != 0 else 0
        lb = 0

    paginator = Paginator(list, 6)
    page_request_variable = 'page'
    page = request.GET.get(page_request_variable)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'results': paginated_queryset,
        'page_request_variable': page_request_variable,
        'lb': lb,
        'la': la,
    }
    return render(request, 'search.html', context)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
    
def post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    category_count_variable = get_category_count()
    tags = Post.objects.filter(id=post.id).values('tags__name', 'tags__slug').annotate(Count('tags__name')).order_by('-tags__name__count')

    ip = get_client_ip(request)
    if ip:
        PostView.objects.get_or_create(ip=ip, post=post)

    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            content_data = form.cleaned_data.get("content")
            parent_obj = None
            try:
                parent_id = int(request.POST.get("parent_id"))
            except:
                parent_id = None
            if parent_id:
                parent_qs = Comment.objects.filter(id=parent_id)
                if parent_qs.exists() and parent_qs.count() == 1:
                    parent_obj = parent_qs.first()
            author = get_author(request.user)
            new_comment, created = Comment.objects.get_or_create(
                author=author,
                post=post,
                content=content_data,
                parent=parent_obj
            )

            return redirect(reverse("post-detail", kwargs={
                'slug': post.slug
            }))

    post_tags_ids = Post.objects.filter(slug=post.slug).values_list('tags', flat=True)
    similar_posts = Post.objects.filter(tags__in=post_tags_ids).exclude(slug=post.slug)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-timestamp')[:4]


    #Edited or not Post
    edited = False
    if post.timestamp.strftime('%Y-%m-%d %H:%M:%S') != post.updated.strftime('%Y-%m-%d %H:%M:%S'):
        edited = True

    visited_user = None
    if request.user.is_authenticated:
        visited_user = get_author(request.user)     

    context = {
        'blog': post,
        'form': form,
        'edited': edited,
        'similar_posts': similar_posts,
        'category_count': category_count_variable,
        'tags': tags,
        'visited_user': visited_user
    }
    return render(request, 'post.html', context)

@login_required(login_url='/accounts/login/')
def post_create(request):
    title = 'Create'
    form = PostForm(request.user, request.POST or None, request.FILES or None)
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'slug': form.instance.slug
            }))
    context = {
        'title': title,
        'form': form
    }
    return render(request, 'post_create.html', context)

@login_required(login_url='/accounts/login/')
def post_update(request, slug):
    title = 'Update'
    post = get_object_or_404(Post, slug=slug)
    form = PostForm(
        request.user,
        request.POST or None,
        request.FILES or None,
        instance=post
    )
    author = get_author(request.user)
    if author != post.author:
        return redirect('/blogs')
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'slug': form.instance.slug
            }))

    context = {
        'title': title,
        'form': form
    }
    return render(request, 'post_create.html', context)

@login_required(login_url='/accounts/login/')
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    author = get_author(request.user)
    if author != post.author:
        return redirect('/blogs')
    post.delete()
    return redirect(reverse("blog-list"))

def trending(request):
    d = date.today() - timedelta(days=60)

    trending = Post.objects.filter(status='public', date__gte=d)

    views = PostView.objects.filter(post__in=[p for p in trending]).values("post").annotate(post_count=Count('post')).order_by('-post_count')

    pk_list = [v['post'] for v in views]

    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])

    queryset = Post.objects.filter(pk__in=pk_list).order_by(preserved)

    paginator = Paginator(queryset, 8)
    page_request_variable = 'page'
    page = request.GET.get(page_request_variable)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'article_list': paginated_queryset,
        'page_request_variable': page_request_variable
    }
    return render(request, 'trending.html', context)

def latest(request):
    latest = Post.objects.filter(status='public').order_by('-timestamp')

    paginator = Paginator(latest, 9)
    page_request_variable = 'page'
    page = request.GET.get(page_request_variable)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'article_list': paginated_queryset,
        'page_request_variable': page_request_variable
    }

    return render(request, 'latest.html', context)

@login_required(login_url='/accounts/login/')
def delete_comment(request):
    id = request.GET.get('id')
    try:
        comment = Comment.objects.filter(id=int(id))[0]
        slug = comment.post.slug
        if comment.author.user == request.user:
            try:
                comment.delete()
                return redirect(reverse('post-detail', kwargs={
                    'slug': slug
                }))
            except:
                return redirect(reverse('post-detail', kwargs={
                    'slug': slug
                }))
    except:
        return redirect(reverse('blog-list'))
    
    
@login_required(login_url='/accounts/login/')
def like_unlike_post(request):
    user = request.user
    if request.method == 'POST':
        post_slug = request.POST.get('post_slug')
        status = request.POST.get('status')
        post_obj = Post.objects.get(slug=post_slug)
        author = get_author(user)

        if author in post_obj.liked.all():
            post_obj.liked.remove(author)
        else:
            post_obj.liked.add(author)

        Like.objects.get_or_create(user=author, post=post_obj, value='Like')

        if status == ' Unlike':
            like_obj = Like.objects.filter(user=author, post=post_obj)
            like_obj.delete()

    return redirect(reverse("post-detail", kwargs={
        'slug': post_slug
    }))