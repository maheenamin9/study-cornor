from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Room, Topic, Message, User
from .forms import RoomForm, MessageForm, UserForm, MyUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect

def signInView(request):
    page='signIn'
    # if already login, then restrict user to home page instead of sign in
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        # getting form values
        email = request.POST.get('email')
        password = request.POST.get('password')
        # check if user already exists or not
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')
        # if exists, authenticate its credentials
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid email address or password')
    context = {'page': page}
    return render(request, "base/loginRegister.html", context)

def signUpView(request):
    # creating a form instance
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        print(form)
        if form.is_valid():
            # get the instance from form but only in 'memory' not in 'database' to make some changes before saving
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An error occured during registration")
    context={'form': form}
    return render(request, "base/loginRegister.html", context)

def signOutView(request):
    logout(request)
    return redirect('signIn')

def home(request):
    # query the database 
    # rooms = Room.objects.all()
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # filter out the search
    rooms = Room.objects.filter(
        Q(topic__name__icontains = q) | 
        Q(name__icontains = q) | 
        Q(description__icontains = q)
    )
    # count the filtered value
    roomCount = rooms.count()
    topics = Topic.objects.all()[0:4]
    roomMessages = Message.objects.filter(
        Q(room__topic__name__icontains = q)
    )
    context = {'rooms': rooms, 'topics': topics, 'roomCount': roomCount, 'roomMessages': roomMessages}
    return render(request, "base/home.html", context)

def room(request, pk):
    # query the database to get specific room
    room = Room.objects.get(id=pk)
    # query to get the messages(child object) of specific room | many to one relationship
    roomMessages = room.message_set.all()
    # query to get the participants(child objects) of specific room | many to many relationship
    participants = room.participants.all()
    if request.method == 'POST':
        # saving data in message model
        Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        # add user to participants list
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'roomMessages': roomMessages, 'participants': participants}
    return render(request, "base/room.html", context)

@login_required(login_url="signIn")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        # before
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit = False)
        #     room.host = request.user
        #     room.save()
        #     return redirect('home')

        topicName = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topicName)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')
    context = {'form': form, 'topics': topics}
    return render(request, "base/roomForm.html", context)

@login_required(login_url="signIn")
def updateRoom(request, pk):
    # query database
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    # restrict user to update room of another user
    if request.user != room.host:
        return HttpResponse("You are not allowed to update room of another user")
    if request.method == "POST":
        # before
        # form = RoomForm(request.POST, instance=room)  # update the room
        # if form.is_valid():
        #     form.save()
        #     return redirect('home')

        topicName = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topicName)
        room.topic = topic
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    context = {'form': form, 'room': room}
    return render(request, "base/roomForm.html", context)

@login_required(login_url="signIn")
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    # restrict user to delete room of another user
    if request.user != room.host:
        return HttpResponse("You are not allowed to delete room of another user")
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {'object': room}
    return render(request, "base/delete.html", context)

@login_required(login_url="signIn")
def updateMessage(request, pk):
    message = Message.objects.get(id=pk)
    form = MessageForm(instance=message)
    if request.user != message.user:
        return HttpResponse("You are not allowed to update message of another user")
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('room', pk=message.user.id)
            # return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    context = {'form': form}
    return render(request, "base/updateMessage.html", context)

@login_required(login_url="signIn")
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    # restrict user to delete message of another user
    if request.user != message.user:
        return HttpResponse("You are not allowed to delete message of another user")
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    context = {'object': message}
    return render(request, "base/delete.html", context)

@login_required(login_url='signIn')
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    topics = Topic.objects.all()
    rooms = user.room_set.all()
    roomMessages = user.message_set.all()
    context = {'user': user, 'topics': topics, 'rooms': rooms, 'roomMessages': roomMessages}
    return render(request, "base/profile.html", context)

@login_required(login_url='signIn')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('userProfile', pk=user.id)
        else:
            messages.error(request, 'Invalid')
    context = {'form': form}
    return render(request, 'base/updateUser.html', context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics': topics}
    return render(request, 'base/topics.html', context)

def activityPage(request):
    roomMessages = Message.objects.all()
    context = {'roomMessages': roomMessages}
    return render(request, 'base/activity.html', context)