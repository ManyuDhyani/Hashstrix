from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.mail import send_mail
from smtplib import SMTPRecipientsRefused, SMTPServerDisconnected
from django.urls import reverse
from django.contrib import messages

from blog.models import Post
from .forms import SendPostForm
from .models import HowItWorks, TermsCondition, CommunityGuidelines, PrivacyPolicy, Announcement
from hashstrix.settings import EMAIL_HOST_USER

def post_share(request, slug):
    get_post = get_object_or_404(Post, slug=slug)
    URL = "https://hashstrix.com" + get_post.get_absolute_url()
    sent = 0
    if request.method == 'POST':
        form = SendPostForm(request.POST)
        if form.is_valid():
            to = form.cleaned_data['to']
            message = form.cleaned_data['message']
            name = form.cleaned_data['name']
            to = to.split(',')
            if name == '':
                if request.user.is_authenticated:
                    subject = "<no-reply HashStrix> | Blog Shared by" + " " + request.user.username
                else:
                    subject = "<no-reply HashStrix> | Blog Shared Anonymously."
            else:
                subject = "<no-reply HashIt> | Blog Shared by " + name
            Email = EMAIL_HOST_USER

            if message:
                msg = "Title: " + get_post.title + "\nAuthor: " + get_post.author.user.username + "\nURL to Post: " + URL + "\nMessage From sender: " + message
            else:
                msg = "Title: " + get_post.title + "\nAuthor: " + get_post.author.user.username + "\nURL to Post: " + URL

            try:
                sent = send_mail(subject, msg, Email, to)
            except SMTPRecipientsRefused:
                messages.error(request, "Please Enter Email correctly.")
            except SMTPServerDisconnected:
                messages.error(request, "Please check the Internet connection and Try Again!")
            except:
                messages.error(request, "Post shared unsuccessfully.")

            if sent:
                messages.success(request, "You have successfully shared the post.")
                return redirect(reverse("share", kwargs={
                    'slug': slug
                }))

    else:
        form = SendPostForm()

    context = {
        'form': form,
        'post': get_post
    }

    return render(request, 'sharepost.html', context)


def how_it_works(request):
    obj = HowItWorks.objects.first()
    return render(request, 'howitworks.html', {'obj': obj})

def terms_condition(request):
    obj = TermsCondition.objects.first()
    return render(request, 'TermsCondition.html', {'obj': obj})

def community_guidelines(request):
    obj = CommunityGuidelines.objects.first()
    return render(request, 'CommunityGuidelines.html', {'obj': obj})

def privacy_policy(request):
    obj = PrivacyPolicy.objects.first()
    return render(request, 'PrivacyPolicy.html', {'obj': obj})
    
def announcements(request):
    obj = Announcement.objects.first()
    return render(request, 'announcement.html', {'obj': obj})

def plain_text_view(request):
    file = open("/home/manyu/hashstrixdir/static/ads.txt", 'r')
    content = file.read()
    file.close()
    return HttpResponse(content, content_type='text/plain')