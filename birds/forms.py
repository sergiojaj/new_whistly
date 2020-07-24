from django import forms
from .models import Bird, Comment, Reply

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

class AddBirdForm(forms.ModelForm):
    
    class Meta:
        model = Bird
        fields = ('species','location','picture','photographer_comment')

        widgets = {
                    "species": forms.TextInput(attrs={'class': 'form-control'}),
                    "location": forms.TextInput(attrs={'class': 'form-control'}),
                    "picture": forms.FileInput(attrs={"type":"file", "class":"form-control-file"}),
                    "photographer_comment": forms.Textarea(attrs={'class': 'form-control', "style":"height:80px"})
                }