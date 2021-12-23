from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    overview = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'maxlength': '400',
        'placeholder': 'Blog summary which help to attract more readers to read your blogs. (Character limit 400) Optional',
    }),)
    thumbnail = forms.ImageField(widget=forms.FileInput, )
    class Meta:
        model = Post
        fields = ('title', 'overview', 'content', 'thumbnail',
                  'category', 'previous_post', 'next_post', 'tags', 'status')

    def __init__(self, user, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'maxlength': '100',
            'placeholder': 'Blog Title (Character limit 100)'
        })
        self.fields['previous_post'].queryset = Post.objects.filter(author__user=user)
        self.fields['next_post'].queryset = Post.objects.filter(author__user=user)

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        tags = set([tag.lower() for tag in tags])
        return tags

class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Type your comment ....',
        'id': 'usercomment',
        'rows': '4'
    }))

    class Meta:
        model = Comment
        fields = ('content', )
    
    def __init__(self, *args, **kwargs):
      super(CommentForm, self).__init__(*args, **kwargs)
      self.fields['content'].label = "Reply"
