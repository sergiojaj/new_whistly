from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy

from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormMixin
from django.views.generic.detail import SingleObjectMixin
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model, get_user

from django.db.models import Q

from birds.models import Bird, Comment, Reply, Seed
from birds.forms import CommentForm, ReplyForm

# Create your views here.
#### Basic Views
class HomeTemplateView(TemplateView):
    template_name = 'home.html'

class RemoveAccountDeleteView(LoginRequiredMixin,DeleteView):
    model = get_user_model()
    template_name = 'account/remove_account.html'
    success_url = reverse_lazy('home')

##### Profiles related Views

class ProfileDetailView(LoginRequiredMixin,DetailView):
    model = get_user_model()
    template_name = 'profile/profile_detail.html'
    context_object_name = 'profile'
    
class ProfileUpdateView(LoginRequiredMixin,UpdateView):

    model = get_user_model()
    template_name = 'profile/profile_edit.html'
    fields = ('profile_picture', 'about_user',)
    
##### Bird App related Views

class BirdsNestListView(ListView):
    model = Bird
    template_name = 'bird/bird_list.html'
    context_object_name = 'birds_list'
    # pagination is easy
    paginate_by = 9


class BirdDetailView(LoginRequiredMixin, DetailView):
    model = Bird
    template_name = 'bird/bird_detail.html'
    context_object_name = 'bird_detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['reply_form'] = ReplyForm()
        return context

class BirdDetailCommentFormView(LoginRequiredMixin,SingleObjectMixin, FormView):
    model = Bird
    template_name = 'bird/bird_detail.html'
    form_class = CommentForm
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.comment_creator = self.request.user
        form.instance.bird = self.object
        if form.instance.comment_creator == self.object.photographer:
            form.instance.comment_approved = True
            form.save()
        else:
            form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('bird_detail', kwargs={'pk':self.object.pk})


class BirdDetailReplyFormView(LoginRequiredMixin,SingleObjectMixin, FormView):
    model = Comment
    template_name = 'bird/bird_detail.html'
    form_class = ReplyForm
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = ReplyForm(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.reply_creator = self.request.user
        form.instance.comment = self.object
        if form.instance.reply_creator == self.object.comment_creator or form.instance.reply_creator == self.object.bird.photographer:
            form.instance.reply_approved = True
            form.save()
        else:
            form.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('bird_detail', kwargs={'pk':self.object.bird.pk})


class BirdDetailSimpleView(LoginRequiredMixin,View):
    
    def get(self, request, *args, **kwargs):
        view = BirdDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.POST.get('comment', False):
            view = BirdDetailCommentFormView.as_view()
            return view(request, *args, **kwargs)
        elif request.POST.get('reply', False):
            view = BirdDetailReplyFormView.as_view()
            return view(request, *args, **kwargs)


############### This function view does the same as the 4 CBVs above () ####################
# def bird_detail_forms(request, pk):
#     if request.method=='POST':
#         if request.POST.get('comment', False):
#             bird_detail = get_object_or_404(Bird, pk=pk)
#             form = CommentForm(request.POST)
#             if form.is_valid():
#                 comment = form.save(commit=False)
#                 comment.bird = bird_detail
#                 comment.comment_creator = request.user
#                 if comment.comment_creator == bird_detail.photographer:
#                     comment.comment_appvoed = True
#                     comment.save()
#                 else:
#                     comment.save()
#                 return redirect('bird_detail', pk=bird_detail.pk)
#         elif request.POST.get('reply', False):
#             single_comment = get_object_or_404(Comment, pk=pk)
#             form = ReplyForm(request.POST)
#             if form.is_valid():
#                 reply = form.save(commit=False)
#                 reply.comment = single_comment
#                 print(request.user)
#                 reply.reply_creator = request.user
#                 if reply.reply_creator == single_comment.comment_creator:
#                     reply.comment_approved = True
#                     reply.save()
#                 else:
#                     reply.save()
#                 return redirect('bird_detail', pk=single_comment.bird.pk)
#     else:
#         bird_detail = get_object_or_404(Bird, pk=pk)
#         comment_form = CommentForm()
#         reply_form = ReplyForm()
#     return render(request, 'bird/bird_detail.html', {'bird_detail':bird_detail,
#                     'comment_form':comment_form,
#                     'reply_form':reply_form})


class BirdUpdateView(LoginRequiredMixin,UpdateView):
    model = Bird
    template_name = 'bird/bird_update.html'
    fields = ('species', 'location', 'photographer_comment',)


class BirdDeleteView(LoginRequiredMixin,DeleteView):
    model = Bird
    template_name = 'bird/bird_delete.html'
    success_url = reverse_lazy('birds_nest')


class AddBirdCreateView(LoginRequiredMixin,CreateView):
    model = Bird
    template_name = 'bird/add_bird.html'
    fields = ['species', 'location', 'picture', 'photographer_comment']

    def form_valid(self, form):
        form.instance.photographer = self.request.user
        return super(AddBirdCreateView, self).form_valid(form)

##### comment cbvs

class EditCommentUpdateView(LoginRequiredMixin,UpdateView):
           
    model = Comment
    fields = ('comment',)
    template_name = 'comment_reply/comment_reply_update.html'
    
    def get_success_url(self):
        return reverse('bird_detail', kwargs={'pk':self.object.bird.pk})


class EditReplyUpdateView(LoginRequiredMixin,UpdateView):
    model = Reply
    fields = ('reply',)
    template_name = 'comment_reply/comment_reply_update.html'
    
    def get_success_url(self):
        return reverse('bird_detail', kwargs={'pk':self.object.comment.bird.pk})


# Seed function view
# def add_remove_seed_function_view(request, *args, **kwargs):
#     """
#     THIS FUNC VIEW HAS BEEN REPLACED BY A CBV
#     """
#     bird = get_object_or_404(Bird, pk=kwargs['pk'])
#     """
#     query I need to write:
#         select seeded from seed where seeder_id = user and bird_id = bird_pk
#         user clicks on seed btn:
#             if returns true, means user wants to remove seed
#             if returns false, means user wants to add seed
#     Seed.objects.values_list('seeded').filter(seeder__username='diego').filter(bird__species='Brown Matuque')
#     """
#     if request.method=='GET':
#         seeded = Seed.objects.values_list('seeded').filter(seeder__username=request.user).filter(bird__species=bird.species)
#         # print(str(seeded.query)) to see the sql query generated
#         if seeded:
#             seed = Seed.objects.filter(seeder__username=request.user).filter(bird__species=bird.species)
#             seed.delete()
#             return redirect('bird_detail', pk=bird.pk)
#         else:
#             seed = Seed()
#             seed.seeded = True
#             seed.bird = bird
#             seed.seeder = request.user
#             seed.save()
#             return redirect('bird_detail', pk=bird.pk)


class Seed_Add_Remove_View(View):
    def get(self, request, *args, **kwargs):
        bird = get_object_or_404(Bird, pk=kwargs['pk'])
        seeded = Seed.objects.values_list('seeded').filter(
                                                seeder__username=request.user).filter(
                                                    bird__species=bird.species)
        if seeded:
            seed = Seed.objects.filter(
                                        seeder__username=self.request.user).filter(
                                        bird__species=bird.species)
            seed.delete()
            return redirect('bird_detail', pk=bird.pk)
        else:
            seed = Seed()
            seed.seeded = True
            seed.bird = bird
            seed.seeder = self.request.user
            seed.save()
            return redirect('bird_detail', pk=bird.pk)
        return super().get(request, *args, **kwargs)


##### search

class SearchResultsListView(LoginRequiredMixin, ListView):
    model = Bird
    template_name = 'search_results.html'
    context_name = 'bird_list'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        return Bird.objects.filter(
             Q(photographer__username__icontains=query)| Q(species__icontains=query)
             | Q(photographer_comment__icontains=query) | Q(location__icontains=query)
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_search"] = self.request.GET.get('q')
        return context       
        


###### function based views
### hopefuly learn cbvs enough to not need to use these
## protect these with login_required decorator

def approve_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.comment_approved = True
    comment.save()
    return redirect('bird_detail', pk=comment.bird.pk)

def remove_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment_pk = comment.bird.pk
    comment.delete()
    return redirect('bird_detail', pk=comment_pk)

def approve_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    reply_pk = reply.comment.bird.pk
    reply.reply_approved = True
    reply.save()
    return redirect('bird_detail', pk=reply_pk)

def remove_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    reply_pk = reply.comment.bird.pk
    reply.delete()
    return redirect('bird_detail', pk=reply_pk)