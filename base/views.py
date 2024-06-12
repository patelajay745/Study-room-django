from django.shortcuts import render,redirect
from .models import Room
from .forms import RoomForm


# Create your views here.

def home(request):
    
    context={'rooms':Room.objects.all}
    return render(request,'base/home.html',context)

def room(request,pk):
    context={'room':Room.objects.get(id=pk)}
    return render(request,'base/room.html',context)

def createRoom(request):
    form=RoomForm()
    if request.method=='POST':
        form=RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context={'form':form}
    return render(request,'base/room_form.html',context)