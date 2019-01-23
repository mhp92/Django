import datetime

from django.db.models import Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse


from .models import Choice, Poll, Vote

from .forms import PollForm, EditPollForm, ChoiceForm

# Create your views here.


@login_required
def polls_list(request):
	"""
	Renders the polls_list.html template which list 
	all the currently available polls
	"""
	polls = Poll.objects.all()
	search_term=''

	# modify the the queryset before we pass t in the paginator

	if 'text' in request.GET:
		polls = polls.order_by('text')


	if 'pub_date' in request.GET:
		polls = polls.order_by('-pub_date')

						# num_votes is not a column in our models
	if 'num_votes' in request.GET:
		polls = polls.annotate(Count('vote')).order_by('-vote__count')


	if 'search' in request.GET:
		search_term = request.GET['search']
		polls=polls.filter(text__icontains=search_term) 

	paginator = Paginator(polls, 5)

	page = request.GET.get('page')
	polls = paginator.get_page(page)

	get_dict_copy = request.GET.copy()
	params = get_dict_copy.pop('page', True) and get_dict_copy.urlencode()

	context = {'polls': polls, 'params': params, 'search_term': search_term}
	return render(request, 'polls/polls_list.html', context)


def my_polls(request):
	# my_polls = Poll.objects.filter(owner=request.user)
	# print(my_polls)
	# This is the same as above
	my_polls = request.user.poll_set.all()
	# print(my_polls)
	paginator = Paginator(my_polls, 5)

	page = request.GET.get('page')
	my_polls = paginator.get_page(page)


	context = {'my_polls':my_polls}
	return render(request, 'polls/my_polls.html', context)



@login_required
def add_poll(request):
	if request.method == 'POST':
		form = PollForm(request.POST)
		if form.is_valid():
			new_poll = form.save(commit=False)
			new_poll.pub_date = datetime.datetime.now()
			new_poll.owner = request.user
			new_poll.save()
			new_choice1 = Choice(
									poll = new_poll,
									choice_text = form.cleaned_data['choice1']
								).save()
			new_choice2 = Choice(
									poll = new_poll,
									choice_text = form.cleaned_data['choice2']
								).save()
			messages.success(
								request, 
								'Poll and Choices added!', 
								extra_tags='alert alert-success alert-dismissible fade show')
			return redirect('polls:my_polls')

	else:	
		form = PollForm()
	context = {'form': form}
	return render(request, 'polls/add_poll.html', context)



@login_required
def edit_poll(request, poll_id):
	poll = get_object_or_404(Poll, id=poll_id)
	if request.user != poll.owner:
		return redirect('/')

	if request.method == "POST":
		form = EditPollForm(request.POST, instance=poll)
		if form.is_valid():
			new_poll = form.save(commit=False)
			new_poll.pub_date = datetime.datetime.now()
			form.save()
			messages.success(
								request, 
								'Poll was successfully changed!', 
								extra_tags='alert alert-success alert-dismissible fade show')
			return redirect('polls:list')


	else:
		form = EditPollForm(instance=poll)

	return render(request, 'polls/edit_poll.html', {'form': form, 'poll':poll})




@login_required
def delete_poll(request, poll_id):
	
	poll = get_object_or_404(Poll, id=poll_id)
	if request.user != poll.owner:
		return redirect('/')

	if request.method == 'POST':
		poll.delete()
		messages.success(
								request, 
								'Poll was successfully deleted!', 
								extra_tags='alert alert-success alert-dismissible fade show')
			
			
		return redirect('polls:list')
		

	return render(request, 'polls/delete_poll_confirm.html', {'poll':poll})



@login_required
def add_choice(request, poll_id):
	poll = get_object_or_404(Poll, id=poll_id)
	if request.user != poll.owner:
		return redirect('/')

	if request.method == "POST":
		form = ChoiceForm(request.POST)
		if form.is_valid():
			new_choice = form.save(commit=False)
			new_choice.poll = poll
			new_choice.save()
			messages.success(
								request, 
								'Choice was successfully added!', 
								extra_tags='alert alert-success alert-dismissible fade show')
			return HttpResponseRedirect(reverse("polls:edit_poll", args=(poll_id,)))

	else:
		form = ChoiceForm()

	return render(request, 'polls/add_choice.html', {'poll':poll, 'form':form})



@login_required
def edit_choice(request, choice_id):
	choice = get_object_or_404(Choice, id=choice_id)

	poll = get_object_or_404(Poll, id=choice.poll.id)
	if request.user != poll.owner:
		return redirect('/')

	if request.method == "POST":
		form = ChoiceForm(request.POST, instance=choice)
		if form.is_valid():
			form.save()
			messages.success(
								request, 
								'Choice was successfully changed!', 
								extra_tags='alert alert-success alert-dismissible fade show')
			
			# change redirect to another path (polls:edit)
			return HttpResponseRedirect(reverse("polls:edit_poll", args=(poll.id,)))



	else:
		form = ChoiceForm(instance=choice)

	return render(request, 'polls/edit_choice.html', {'form': form, 'choice': choice})


@login_required
def delete_choice(request, choice_id):
	choice = get_object_or_404(Choice, id=choice_id)
	poll = get_object_or_404(Poll, id=choice.poll.id)
	if request.user != poll.owner:
		return redirect('/')

	if request.method == 'POST':
		choice.delete()
		messages.success(
								request, 
								'Choice was successfully deleted!', 
								extra_tags='alert alert-success alert-dismissible fade show')
			
			
		return HttpResponseRedirect(reverse("polls:edit_poll", args=(poll.id,)))
		

	return render(request, 'polls/delete_choice_confirm.html', {'choice':choice})



@login_required
def poll_detail(request, poll_id):
	"""

	Render the poll_detail.html which allows a user to vote on the coices of a poll

	"""
	# poll = Poll.objects.get(id=poll_id)  // DoesNotExist
	poll = get_object_or_404(Poll, id=poll_id)
	user_can_vote = poll.user_can_vote(request.user)
	results = poll.get_results_dict()
	context = {'poll': poll, 'user_can_vote': user_can_vote,  'results': results}
	return render(request, 'polls/poll_detail.html', context)



@login_required
def poll_vote(request, poll_id):
	poll = get_object_or_404(Poll, id=poll_id)

	if not poll.user_can_vote(request.user):
		messages.error(request, 'You have already votted on this Poll!')
		return redirect('polls:detail', poll_id=poll_id)
		
	choice_id = request.POST.get('choice')
	if choice_id:
		choice = Choice.objects.get(id=choice_id)
		new_vote = Vote(user=request.user, poll=poll, choice=choice)
		new_vote.save()
		messages.success(
								request, 
								'You successfully voted!', 
								extra_tags='alert alert-success alert-dismissible fade show')
			
		
	else:
		messages.error(request, 'Please Select something!', extra_tags='alert alert-danger alert-dismissible fade show')
		return redirect('polls:detail', poll_id=poll_id)
	return redirect('polls:detail', poll_id=poll_id)
	
	


















