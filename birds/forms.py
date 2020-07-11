from django import forms
from .models import Comment, Reply

class CommentForm(forms.ModelForm):

    comment = forms.CharField(widget=forms.Textarea(
        attrs={'rows':5, 
        'placeholder':'Enter a beautiful comment here!'}
    ), 
                                help_text='The max lenght is 600 characters.',
                                max_length=600,)
    
    class Meta:
        model = Comment
        fields = ['comment']

class ReplyForm(forms.ModelForm):

    reply = forms.CharField(widget=forms.Textarea(
        attrs={'rows':3, 
        'placeholder':'Enter a reply here!'}
    ), max_length=600,)

    class Meta:
        model = Reply
        fields = ['reply']