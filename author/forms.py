from django import forms
from django.contrib.auth import get_user_model

from .models import Profile
from blog.models import Author

class ProfileForm(forms.ModelForm):
    bio = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control autosize',
        'placeholder': 'Write something about you (Optional)',
        'id': 'bio',
        'rows': '4',
    }), required=False)
    class Meta:
        model = Profile
        fields = ('bio', 'link1', 'link2', 'linkedin', 'youtube', 'location')

User = get_user_model()

class AcountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')

class ProfilePictureForm(forms.ModelForm):
    profile_picture = forms.ImageField(widget=forms.FileInput, required=False)
    class Meta:
        model = Author
        fields = ('profile_picture',)