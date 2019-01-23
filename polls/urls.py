
from django.urls import path

from . import views


app_name="polls"

urlpatterns = [
    path('list/', views.polls_list, name="list"),
    path('list/my_polls/', views.my_polls, name="my_polls"),
    path('add_poll/', views.add_poll, name="add_poll"),
    path('edit/<int:poll_id>/', views.edit_poll, name="edit_poll"),
    path('edit/<int:poll_id>/choice/add/', views.add_choice, name="add_choice"),
    path('edit/choice/<int:choice_id>/', views.edit_choice, name="edit_choice"),
    path('delete/choice/<int:choice_id>/', views.delete_choice, name="delete_choice_confirm"),
    path('delete/poll/<int:poll_id>/', views.delete_poll, name="delete_poll_confirm"),
    # polls/details/1/
    path('details/<int:poll_id>/', views.poll_detail, name='detail'),
    # polla/detail/1/vote
    path('details/<int:poll_id>/vote/', views.poll_vote, name='vote')
]
