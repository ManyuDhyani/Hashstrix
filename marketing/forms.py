from django import forms

class SendPostForm(forms.Form):
    to = forms.CharField(max_length=50, label='to', widget=forms.TextInput(attrs={
        'placeholder': 'john@gmail.com'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Any additional message (Optional)'
    }), label='Additional Message', required=False)
    name = forms.CharField(max_length=50, label='name', required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Your Name (Optional)'
    }))