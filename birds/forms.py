from django import forms
from .models import Bird, Comment, Reply

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(
                attrs={
                        'rows':5, 
                        'placeholder':'Enter a beautiful comment here!', 
                        'id':'comment-text'},
                        )}
                
class ReplyForm(forms.ModelForm):
    
    class Meta:

        model = Reply
        fields = ('reply',)
        widgets = {
            
                'reply': forms.TextInput(attrs={
                    'rows':3,
                    'placeholder': 
                    'Enter a reply here!'})}

class AddBirdForm(forms.ModelForm):
    
    class Meta:
        model = Bird
        fields = ('species','location','picture','photographer_comment')

        widgets = {
                    "species": forms.TextInput(attrs={'class': 'form-control'}),
                    "location": forms.TextInput(attrs={'class': 'form-control'}),
                    "picture": forms.FileInput(attrs={"type":"file", "class":"form-control-file"}),
                    "photographer_comment": forms.Textarea(attrs={'class': 'form-control', "style":"height:80px mt-2"})
                }