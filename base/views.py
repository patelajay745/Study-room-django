from django.shortcuts import render,redirect,HttpResponse
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import RoomForm,RegisterForm
from django.db.models import Count
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout



# Create your views here.

def loginPage(request):

    page="login"

    if request.user.is_authenticated:
        return redirect('home')
    if request.method== 'POST':
        username= request.POST.get('username').lower()
        password=request.POST.get('password')
        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request,"user does not exists")

        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else: 
            messages.error(request,"User or Password does not exists")

    context={"page": page}  
    return render(request,'base/login_register.html',context)


def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    form= RegisterForm()
    context={"form": form}

    if request.method=="POST":
        form=RegisterForm(request.POST)
        if form.is_valid():
                user=form.save(commit=False)
                user.username=user.username.lower()
                user.save()
                # messages.success("Register Sucessfully. Now you can login")
                login(request,user)
                return redirect('home')
        else:
                messages.error(request,form.errors)
            

    return render(request,"base/login_register.html",context)


def home(request):

    q=request.GET.get('q')
    if q is not None:
        room=Room.objects.filter(Q(topic__name__icontains=q) |
                                 Q(name__icontains=q) |
                                 Q(host__username__icontains=q) |
                                 Q(description__icontains=q))
    else:
        room=Room.objects.all()

    room_count=room.count() #faster then len method
    # roomcount=len(room)
    
    pupularTopic=Topic.objects.annotate(room_count=Count('room')).order_by('-room_count')[:10]
    context={'rooms':room,'topics':pupularTopic,"room_count":room_count}    
    return render(request,'base/home.html',context)

def room(request,pk):
    room=Room.objects.get(id=pk)
    room_messages=room.message_set.all().order_by('-created')
    context={'room':room,'room_messages':room_messages}
    return render(request,'base/room.html',context)

@login_required(login_url='login')
def createRoom(request):
    form=RoomForm()
    if request.method=='POST':
        form=RoomForm(request.POST)
        if form.is_valid():
            room=form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')

    context={'form':form}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def updateRoom(request,pk):
    room=Room.objects.get(id=pk)
    form=RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse("You are not authorized")

    if request.method=='POST':
        form=RoomForm(request.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context={'form':form}
    return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room=Room.objects.get(id=pk)
    if request.method=='POST':
        room.delete()
        return redirect('home')
    context={'room':room}
    return render(request,'base/delete_room.html',context)
