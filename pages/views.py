from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy

from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormMixin
from django.views.generic.detail import SingleObjectMixin
from django.views import View
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model, get_user

from allauth.account.views import PasswordChangeView

from django.db.models import Q, Count

from birds.models import Bird, Comment, Reply, Seed
from birds.forms import CommentForm, ReplyForm, AddBirdForm

# Create your views here.
#### Basic Views
class HomeTemplateView(TemplateView):
    template_name = 'home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            trending = Bird.objects.annotate(num_seed=Count('seeds')).order_by('-num_seed')[:6]
            latest = Bird.objects.all()[:6]
        except Exception:
            trending = Bird.objects.all()[:6]
            latest = Bird.objects.all()[:6]
        context['trending_birds'] = trending
        context['latest_birds'] = latest
        return context

class RemoveAccountDeleteView(LoginRequiredMixin,DeleteView):
    model = get_user_model()
    template_name = 'account/remove_account.html'
    success_url = reverse_lazy('home')

##### Profiles related Views

class ProfileDetailView(LoginRequiredMixin,DetailView):
    model = get_user_model()
    template_name = 'profile/profile_detail.html'
    context_object_name = 'profile'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gmaps_api_key'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        return context
    
class ProfileUpdateView(LoginRequiredMixin,UpdateView):

    model = get_user_model()
    template_name = 'profile/profile_edit.html'
    fields = ('profile_picture', 'about_user',)

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    Had to overwrite allauth success_url 
    """
    success_url = '/'
    
##### Bird App related Views

class BirdsNestListView(ListView):
    model = Bird
    template_name = 'bird/bird_list.html'
    context_object_name = 'birds_list'
    # pagination is easy
    paginate_by = 9

    def get_queryset(self):
        qs = super().get_queryset()
        order_by = self.request.GET.get('order_by')
        if order_by == 'seeds':
            qs = qs.annotate(num_seed=Count('seeds')).order_by('-num_seed')
        elif order_by == 'species':
            qs = qs.order_by('species')
        elif order_by == 'photographer':
            qs = qs.order_by('photographer__username')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_by'] = self.request.GET.get('order_by','')
        return context

class BirdDetailView(LoginRequiredMixin, DetailView):
    model = Bird
    template_name = 'bird/bird_detail.html'
    context_object_name = 'bird_detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['reply_form'] = ReplyForm()
        from django.conf import settings
        context['gmaps_api_key'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
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
        # Rotation used to be performed via GET. Keep backward-compat but enforce ownership.
        action = request.GET.get('name')
        pk = request.GET.get('pk')
        if action and pk:
            bird_obj = get_object_or_404(Bird, pk=pk)
            if request.user != bird_obj.photographer:
                return redirect('bird_detail', pk=bird_obj.pk)
            if 'rotate-left' in action:
                bird_obj.rotate_left()
            elif 'rotate-right' in action:
                bird_obj.rotate_right()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.POST.get('comment', False):
            view = BirdDetailCommentFormView.as_view()
            return view(request, *args, **kwargs)
        elif request.POST.get('reply', False):
            view = BirdDetailReplyFormView.as_view()
            return view(request, *args, **kwargs)
        elif request.POST.get('rotate', False):
            direction = request.POST.get('direction')
            pk = request.POST.get('pk')
            bird_obj = get_object_or_404(Bird, pk=pk)
            if request.user == bird_obj.photographer:
                if direction == 'left':
                    bird_obj.rotate_left()
                elif direction == 'right':
                    bird_obj.rotate_right()
            return redirect('bird_detail', pk=bird_obj.pk)
        return redirect('bird_detail', pk=kwargs.get('pk'))


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
    form_class = AddBirdForm
    
    # fields = ['species', 'location', 'picture', 'photographer_comment']

    def form_valid(self, form):
        form.instance.photographer = self.request.user
        return super(AddBirdCreateView, self).form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gmaps_api_key'] = getattr(settings, 'GOOGLE_MAPS_API_KEY', '')
        return context

class SupportTemplateView(TemplateView):
    template_name = 'support.html'

class MyBirdsMapView(LoginRequiredMixin, TemplateView):
    template_name = 'map/my_birds_map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Provide the current user's birds with coordinates
        birds = Bird.objects.filter(photographer=self.request.user).exclude(latitude__isnull=True).exclude(longitude__isnull=True)
        context['my_birds'] = birds
        return context

class SuggestSpeciesView(View):
    def post(self, request, *args, **kwargs):
        token = getattr(settings, 'HF_API_TOKEN', '')
        model_id = getattr(settings, 'HF_MODEL_ID', 'microsoft/resnet-50')
        if not token:
            return HttpResponseBadRequest('Model suggestion not configured. Set HF_API_TOKEN env var for free Hugging Face Inference API.')
        if 'image' not in request.FILES:
            return HttpResponseBadRequest('No image provided')
        img_file = request.FILES['image']
        try:
            resp = requests.post(
                f'https://api-inference.huggingface.co/models/{model_id}',
                headers={'Authorization': f'Bearer {token}'},
                data=img_file.read(),
                timeout=25
            )
            resp.raise_for_status()
            data = resp.json()
            # Normalize output: can be list of dicts [{'label':..., 'score':...}]
            suggestions = []
            if isinstance(data, list):
                for item in data[:5]:
                    label = item.get('label')
                    score = item.get('score')
                    if label:
                        suggestions.append({'label': label, 'score': score})
            return JsonResponse({'suggestions': suggestions})
        except Exception as e:
            return HttpResponseBadRequest(f'Failed to suggest species: {e}')

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
    @method_decorator(login_required)
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        bird = get_object_or_404(Bird, pk=kwargs['pk'])
        seeded = Seed.objects.filter(seeder=request.user, bird=bird).exists()
        if seeded:
            seed = Seed.objects.filter(seeder=self.request.user, bird=bird)
            seed.delete()
            return redirect('bird_detail', pk=bird.pk)
        else:
            seed = Seed()
            seed.seeded = True
            seed.bird = bird
            seed.seeder = self.request.user
            seed.save()
            return redirect('bird_detail', pk=bird.pk)
        return redirect('bird_detail', pk=bird.pk)


##### search

class SearchResultsListView(LoginRequiredMixin, ListView):
    model = Bird
    template_name = 'search_results.html'
    paginate_by = 10

    def get_queryset(self):
        """
        A reminder that queryset is equals to Model.objects.all()
        Always add "?q={{ request.GET.q }}&page={{ page_obj.previous_page_number }}" in pagination.
        """
        query = self.request.GET.get('q') # search result
        order_by = self.request.GET.get('order_by') # order by result
        queryset = super().get_queryset() # queryset = Birds.objects

        # to be fixed
        # if search term is entered it will update the queryset from all to specific
        if query:
            queryset = queryset.filter(
                Q(photographer__username__icontains=query)| Q(species__icontains=query)
                | Q(photographer_comment__icontains=query) | Q(location__icontains=query)
            )
        # if order_by link is clicked it will order queryset accordingly
        # using annotate (hidden Django's jewel)
        if order_by:
            if 'comment' in order_by:
                queryset = queryset.filter(comments__comment_approved=True).annotate(num_comment=Count('comments')).order_by('-num_comment')
            elif 'seed' in order_by:
                queryset = queryset.annotate(num_seed=Count('seeds')).order_by('-num_seed')
            elif 'species' in order_by:
                queryset = queryset.order_by('species')
            elif 'photographer' in order_by:
                queryset = queryset.order_by('photographer__username')
            
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_search"] = self.request.GET.get('q')
        return context       

###### function based views
### hopefuly learn cbvs enough to not need to use these
## protect these with login_required decorator

@login_required
@require_POST
def approve_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    # Only the photographer can approve comments on their bird
    if request.user == comment.bird.photographer:
        comment.comment_approved = True
        comment.save()
    return redirect('bird_detail', pk=comment.bird.pk)

@login_required
@require_POST
def remove_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment_pk = comment.bird.pk
    # Photographer or the comment creator may delete
    if request.user == comment.bird.photographer or request.user == comment.comment_creator:
        comment.delete()
    return redirect('bird_detail', pk=comment_pk)

@login_required
@require_POST
def approve_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    reply_pk = reply.comment.bird.pk
    # Only the bird photographer can approve replies
    if request.user == reply.comment.bird.photographer:
        reply.reply_approved = True
        reply.save()
    return redirect('bird_detail', pk=reply_pk)

@login_required
@require_POST
def remove_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    reply_pk = reply.comment.bird.pk
    # Photographer or the reply creator may delete
    if request.user == reply.comment.bird.photographer or request.user == reply.reply_creator:
        reply.delete()
    return redirect('bird_detail', pk=reply_pk)
