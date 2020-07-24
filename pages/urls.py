from django.urls import path
# class based views
from .views import (HomeTemplateView, RemoveAccountDeleteView,
                    ProfileUpdateView, ProfileDetailView, 
                    AddBirdCreateView, BirdsNestListView, BirdUpdateView, BirdDeleteView,BirdDetailSimpleView,
                    EditCommentUpdateView, EditReplyUpdateView,
                    Seed_Add_Remove_View, SearchResultsListView,
                    CustomPasswordChangeView,
                    )
# func based views
from .views import approve_comment, remove_comment, approve_reply, remove_reply

urlpatterns = [
    # basic urls
    path('', HomeTemplateView.as_view(), name='home'),
    path('remove_account/<uuid:pk>/', RemoveAccountDeleteView.as_view(), name='remove_account'),
    
    #profile urls
    path('user_profile/<uuid:pk>/edit/', ProfileUpdateView.as_view(), name='edit_profile'),
    path('user_profile/<uuid:pk>/', ProfileDetailView.as_view(), name='profile_detail'),
    path('accounts/password/change/', CustomPasswordChangeView.as_view(), name='account_change_password'),

    #bird urls
    path('feathers_up/', AddBirdCreateView.as_view(), name='add_bird'),
    path('birds_nest/', BirdsNestListView.as_view(), name='birds_nest'),
    path('birds_nest/<uuid:pk>/', BirdDetailSimpleView.as_view(), name='bird_detail'),
    path('birds_nest/<uuid:pk>/edit/', BirdUpdateView.as_view(), name='bird_update'),
    path('birds_nest/<uuid:pk>/delete/', BirdDeleteView.as_view(), name='bird_delete'),
    
    # comments
    path('birds_nest/<uuid:pk>/comment_approved/', approve_comment, name='comment_approved'),
    path('birds_nest/<uuid:pk>/comment_removed/', remove_comment, name='comment_removed'),
    path('birds_nest/<uuid:pk>/edit_comment/', EditCommentUpdateView.as_view(), name='comment_edit'),

    # replies
    path('birds_nest/<uuid:pk>/reply_approved/', approve_reply, name='reply_approved'),
    path('birds_nest/<uuid:pk>/reply_removed/', remove_reply, name='reply_removed'),
    path('birds_nest/<uuid:pk>/edit_reply/', EditReplyUpdateView.as_view(), name='reply_edit'),
    
    #seeds
    # path('birds_nest/<uuid:pk>/seed', add_remove_seed_function_view, name='seed'),
    path('birds_nest/<uuid:pk>/seed', Seed_Add_Remove_View.as_view(), name='seed'),

    #search
    path('search/', SearchResultsListView.as_view(), name='search_results'),
]

