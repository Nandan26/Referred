from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Room, Company, Message, User, Notification, Application, Selected
from .forms import RoomForm, UserForm, MyUserCreationForm, ApplicationForm

from django.db.models import Count

#for default user model
# from django.contrib.auth.models import User

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse

from django.contrib.auth.forms import UserCreationForm 


#decorators
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator

#for query
from django.db.models import Q

import json

# Create your views here.

def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            users = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

            return render(request, 'base/login-register.html', {'page':page})

        user = authenticate(request, email = email, password = password)

        if user:
            login(request, user)

            return redirect('home')
        
        else:
            messages.error(request, 'Username or password is incorrect')

    context = {
        'page': page
    }
    return render(request,'base/login-register.html', context)

def logout_page(request):
    logout(request) #this will delete the user /the token of perticular session which keeps user logged in
    return redirect('home')

def register_page(request):
    page = 'register'

    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():

            #form.cleaned_data['username'] :- If you want to access any perticular data from the form
            #form.data['username'] :- will return in html tag so better to use cleaned_data

            user = form.save(commit=False)  # do not save the user into the database

            user.username = user.username.lower()

            user.save()
            # user = authenticate(username=username, password=raw_password) 
            login(request, user)

            return redirect('home')
        
        else:
            if form.has_error('username'):
                messages.error(request,'user with this username already exists')
            elif form.has_error('password1'):
                messages.error(request,'Password is too week!!!')
            elif form.has_error('password2'):
                messages.error(request, 'Password entred in both fields are not matching!!')
    
    context = {
        'page': page,
        'form': form
    }
    return render(request,'base/login-register.html', context)

def home(request):

    q = request.GET.get('q') if request.GET.get('q') != None else ''

    #so first it will query the compay with name equals to the value of q and pass to upar flow which means to Room : ex. company__name == company.name
    # rooms = Room.objects.filter(company__name = q)

    #check if name contains specific value given in q or make q == '' if q is not there in the url and when q is '' then it will display all the values
    rooms = Room.objects.filter(
        Q(company__name__icontains = q) |
        Q(position__icontains = q) 
    )

    room_messages = Message.objects.filter(
        Q(room__company__name__icontains=q) | 
        Q(room__position__icontains=q))[0:5]

    room_count = rooms.count()

    paginator = Paginator(rooms, 5)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    # order the company by most number of rooms in descending order
    companies = Company.objects.annotate(num_room=Count("room")).order_by("-num_room")[:5]
    # companies = Company.objects.all()[0:5]

    notifications = []
    notification_number = 0
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user)
        notification_number = len(notifications)

    context = {
        'rooms':page_obj,
        'companies':companies,
        'room_count':room_count,
        'room_msgs':room_messages,
        'notifications':notifications,
        'notification_number':notification_number
    }
    return render(request, 'base/home.html', context)

@login_required(login_url = 'login')
def room(request, room_id):
    
    room = Room.objects.get(id=room_id)
    
    # to get the message (child object) get particular parent object from them get all the childer of that parent object
    #  by using the class name in small_set.all() method
    #for Many to one relationship _set
    room_messages = room.message_set.all().order_by('-created')

    notifications = []
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user)
        notification_number = len(notifications)
    
    #for many to many relationship no need to use _set
    # participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )

        # room.participants.add(request.user)

        # here other parameters are query parameters :- GET request parameters
        return redirect('room',room_id = room.id)

    applications = Application.objects.filter(opportunity_id = room_id)

    try:
        user_application = applications.get(applicant_id = request.user.id)
    except Application.DoesNotExist:
        user_application = None

    already_applied = False
    if user_application :
        already_applied = True
       
    already_selected = Selected.objects.filter(applicant_id=request.user.id).filter(opportunity_id = room_id).exists()
    
    note = ''
    if already_applied:
        note = 'Already applied!!'
    elif already_selected:
        note = 'Congratulations!! Your application is selected for referral'
    
    not_applied = not (already_applied or already_selected)

    skill_set = set()

    if room.skills:
        skills = room.skills.split(',')
        for skill in skills:
            s=skill.strip()
            skill_set.add(s)

    context = {
        'room': room,
        'room_msgs': room_messages,
        # 'participants': participants,
        'notifications':notifications,
        'notification_number':notification_number,
        'not_applied': not_applied,
        'already_applied': already_applied,
        'user_application': user_application,
        'note': note,
        'skills': skill_set
    }

    return render(request, 'base/room.html', context)

def room_details(request, room_id):
    room = Room.objects.get(id=room_id)
    skill_set = set()

    if room.skills :
        skills = room.skills.split(',')
        for skill in skills:
            s=skill.strip()
            skill_set.add(s)
    return render(request, 'base/room-detailspage.html', {'room': room, 'skills': skill_set})


#the below decorator will make sure that this function is called only if user is logged in
# and if user is not logged in it will redirect to login page
@login_required(login_url='login')
def create_room(request):
    companies = Company.objects.all()
    form = RoomForm()
    if request.method == 'POST':
        company_name = request.POST.get('company')
        
        company, created = Company.objects.get_or_create(name = company_name) 

        room = Room.objects.create(
            position = request.POST.get('position'),
            company = company,
            recruiter = request.user,
            description = request.POST.get('description'),
            skills = request.POST.get('skills'),
            experience = request.POST.get('experience'),
            location = request.POST.get('location'),
            link = request.POST.get('link'),
            total_applications = 0
        )
        # line 159 to 165 implementation using the form 
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False) It helps to get model(room) object based on form data

        #     room.recruiter = request.user
            
        #     room.save()

        # return redirect('home')  redirect : here home is taken form name in urls.py of base app
        return redirect('room', room.id)

    # print(companies)
    context = {'form' : form , 'list_companies':companies ,'create': True}
    
    return render(request, 'base/room-form.html', context)

@login_required(login_url='login')
def update_room(request, room_id):
    room = Room.objects.get(id=room_id)

    companies = Company.objects.all()

    form = RoomForm(instance = room)

    if request.user != room.recruiter :
        return HttpResponse('You are not allowed to update this room')

    if request.method == 'POST':
        company_name = request.POST.get('company')
        
        company, created = Company.objects.get_or_create(name = company_name) 

        room.position = request.POST.get('position')
        room.company = company
        room.description = request.POST.get('description')
        room.skills = request.POST.get('skills')
        room.experience = request.POST.get('experience')
        room.location = request.POST.get('location')
        room.link = request.POST.get('link')
        
        room.save()
        return redirect('room',room_id)

    # if RoomForm() -> then it will return empty instance but we can initialize it using room so that while calling update the form is not empty 
    # form = RoomForm(instance = room)
    
    # if request.user != room.recruiter :
    #     return HttpResponse('You are not allowed to update this room')

    # if request.method == 'POST':
    #     form = RoomForm(request.POST, instance=room)
    #     if form.is_valid():
    #         form.save()
    #         return redirect('home')


    context = {'form' : form, 'list_companies': companies, 'room': room, 'create': False}
    return render(request,'base/room-form.html',context)

@login_required(login_url='login')
def delete_room(request, room_id):
    room = Room.objects.get(id = room_id)

    if request.user != room.recruiter :
        return HttpResponse('You are not allowed to update this room')
    if request.method == 'POST':

        room.delete()

        return redirect('home')

    return render(request,'base/delete.html',{'obj': room})

@login_required(login_url='login')
def delete_message(request, msg_id):
    msg = Message.objects.get(id = msg_id)

    if request.user != msg.user :
        return HttpResponse('You are not allowed to delete this message/post')
    
    if request.method == 'POST':

        msg.delete()

        return redirect('home')

    return render(request,'base/delete.html',{'obj': msg})

@login_required(login_url = 'login')
def user_profile(request, user_id):
    context = {}

    user = User.objects.get(id=user_id)

    rooms = user.room_set.all()

    room_msgs = user.message_set.all()[0:5]
    companies = Company.objects.annotate(num_room=Count("room")).order_by("-num_room")[:5]

    followers = user.followers.all()

    is_following = False
    for follower in followers:
        if request.user == follower:
            is_following = True
            break
    
    notifications = []
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user)
        notification_number = len(notifications)
    
    number_of_followers = len(followers)
    following = {}
    if request.user == user:
        following = user.following.all()

    context = {
        'rooms':rooms, 
        'companies':companies,
        'room_msgs':room_msgs,
        'user': user,
        'is_following': is_following,
        'number_of_followers': number_of_followers,
        'notifications':notifications,
        'notification_number':notification_number,
        'following': following
    }
    return render(request,'base/profile.html',context = context)

@login_required(login_url = 'login')
def update_profile(request):
    # user = User.objects.get(id=pk)
    user = request.user

    form = UserForm(instance=user)

    if request.method == 'POST':
        # form = UserForm(request.POST, instance=user)

        form = UserForm(request.POST, request.FILES, instance=user) # for processing files

        if form.is_valid():
            form.save()
            return redirect('user-profile', user_id=user.id)


    return render(request, 'base/edit-user.html', {'form': form})

def comp_page(request):

    q = request.GET.get('q') if request.GET.get('q') != None else ''

    comps = Company.objects.filter(
        Q(name__icontains = q)
    )
    
    return render(request, 'base/companies-page.html', {'comps': comps})

def activity_page(request):
    room_msgs = Message.objects.all()[0:5]
    return render(request, 'base/activity-page.html', {'room_msgs': room_msgs})

def user_activity(request, user_id):
    user = User.objects.get(id=user_id)
    room_msgs = user.message_set.all()[0:5]
    return render(request, 'base/activity-page.html', {'room_msgs': room_msgs})

def following(request):
    user = request.user
    following = {}
    if request.user == user:
        following = user.following.all()
    
    return render(request, 'base/following-listpage.html', {'following_list': following})


@login_required(login_url = 'login')
def add_follower(request,recruiter_id):
    recruiterUser = User.objects.get(id=recruiter_id)

    # followers = recruiterUser.followers.all()

    currUser = request.user

    recruiterUser.followers.add(currUser)

    return redirect('user-profile', user_id = recruiter_id)

@login_required(login_url = 'login')
def remove_follower(request,recruiter_id):
    recruiterUser = User.objects.get(id=recruiter_id)

    # followers = recruiterUser.followers.all()

    currUser = request.user

    recruiterUser.followers.remove(currUser)

    return redirect('user-profile', user_id = recruiter_id)

def view_notifications(request,not_id):
    notification = Notification.objects.get(id=not_id)

    room_id = notification.room.id

    notification.delete()
    
    return redirect('room', room_id=room_id)

@login_required(login_url = 'login')
def apply_now(request, room_id):

    form = ApplicationForm()

    room = Room.objects.filter(id = room_id)
    
    roomobj = room.first()

    if request.method == 'POST':
        application = Application(applicant = request.user, opportunity = roomobj)

        form = ApplicationForm(request.POST, request.FILES, instance = application)
        
        if form.is_valid():
            
            applications = roomobj.total_applications

            room.update(total_applications = applications + 1)

            form.save()

            return redirect('room', room_id = room_id)

        else:
            messages.error(request, "Only .pdf files are allowed")

    return render(request, 'base/apply.html', {'form': form})

@login_required(login_url = 'login')
def update_application(request, application_id):

    application = Application.objects.get(id = application_id)

    form = ApplicationForm(instance= application)
    
    if request.method == 'POST':

        form = ApplicationForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            
            form.save()            
            
            return redirect('room', room_id = application.opportunity.id)
            
    return render(request, 'base/apply.html', {'form': form})

@login_required(login_url = 'login')
def my_applications(request):

    selected_applications = Selected.objects.filter(applicant_id = request.user.id).order_by('-applied')

    pending = Application.objects.filter(applicant=request.user).order_by('-applied')

    notifications = []
    notification_number = 0
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user)
        notification_number = len(notifications)

    return render(request , 'base/my-applications.html', {'selected_application': selected_applications, 'pending': pending, 'notification_number':notification_number, 'notifications':notifications})

@login_required(login_url = 'login')
def view_applications(request, room_id):
    room = Room.objects.get(id = room_id)

    applications = Application.objects.filter(opportunity_id = room_id).order_by('-applied')

    selected = Selected.objects.filter(opportunity_id = room_id).order_by('-applied')

    notifications = []
    notification_number = 0
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user)
        notification_number = len(notifications)
    
    return render(request, 'base/view-applications.html', {'applications': applications ,'selected': selected , 'job': room, 'notification_number':notification_number, 'notifications':notifications})

@login_required(login_url = 'login')
def select_application(request, job_id, can_id):

    room = Room.objects.get(id = job_id)

    applicationRoom = Application.objects.filter(opportunity_id = job_id)

    selectedApplication = applicationRoom.get(applicant_id = can_id)

    user = User.objects.get(id = can_id)

    selected = Selected(opportunity_id = job_id, applicant_id = can_id, resume = selectedApplication.resume, experience = selectedApplication.experience, applied = selectedApplication.applied)
    
    selected.save()
    
    selectedApplication.delete()

    return redirect('applications', room_id = job_id)

@login_required(login_url = 'login')
def reject_application(request, application_id):
    
    application = Application.objects.get(id = application_id)

    room_id = application.opportunity_id

    application.delete()

    return redirect('applications', room_id = room_id)
