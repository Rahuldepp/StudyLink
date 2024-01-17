from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login, logout
from django.contrib import messages
from django.db.models import Q
from .models import * 
from .forms import RoomForm ,UserForm ,MyUserCreationForm

# -------------------------------------------------------------------------
# for login purposes

def loginPage(request):
   page='login'
   if request.user.is_authenticated:
       return redirect('Home')

   if request.method == 'POST':
      email=request.POST.get('email').lower()
      password=request.POST.get('password')
      # print(username)
      # print(password)
      try:
         user=User.objects.get(email=email)
      except Exception:
         messages.error(request,"User does not exist")
         # performing login
      user = authenticate(request,email=email ,password=password)

      if user is not None:
         login(request,user)
         if page_to_load := request.GET.get('next', None):
            print('NEXT:', page_to_load)
            return redirect(page_to_load)
         return redirect("/")
      else:
         messages.error(request,"User name or password is incorrect")
   context={'page':page}
   return render(request,"base/login_register.html",context) 

# ------------------------------------------------------

# register user
def registerPage(request):
    form=MyUserCreationForm()
    if request.method == "POST":
     form=MyUserCreationForm(request.POST)
     if form.is_valid():
        user=form.save(commit=False) 
        user.username=user.username.lower()
        user.save() 
        login(request,user)
        return redirect('/')
     else:
        messages.error(request,'An error occurred during registration')

    return render(request,"base/login_register.html",{'form':form})


# -------------------------------------------------------------------------
# performing logout

def logoutUser(request):
   logout(request)

   return redirect('/')





# -------------------------------------------------------------------------
 
def Home(request):  # sourcery skip: remove-redundant-slice-index
   # getting the value of paremeter (present in url) or    q
   q=request.GET.get('q') if request.GET.get('q')!=None else ''

   # topic __ name = q  here __ shows ( that there is a ForeignKey  key relationship between topic and name) { meant find all rooms who's topic==q}
   rooms=Room.objects.filter(Q(topic__name__icontains=q)|Q(name__icontains=q)|
                             Q(description__icontains=q))
#  to show all present topics
   topics=Topic.objects.all()[0:4]
   room_count=rooms.count()
   room_messages=Message.objects.filter(Q(room__topic__name__icontains=q)).order_by('-created')
   context={'rooms':rooms,'topics':topics,'room_count':room_count,'room_messages':room_messages}
   return render(request,'base/home.html',context)

# -------------------------------------------------------------------------

# for room--
def room(request ,pk):
   room=Room.objects.get(id= pk)
   # getting all the messages related to room
   room_messages=room.message_set.all().order_by('-created')
   participants=room.participants.all() 

   if request.method == 'POST':
      

      message=Message.objects.create(
         user=request.user,
         room=room,
         body=request.POST.get('body'),

      ) 
      # first add a user if someone is trying  to comment
      room.participants.add(request.user)
      # here Room is the name of views.room function 
      return redirect('Room',pk=room.id)

   context={'room':room,'room_messages':room_messages,'participants':participants}

   return render (request,"base/room.html",context)


# --------------------------------------------------------
# user profile

def userProfile(request,pk):
   user=User.objects.get(id=pk)
   # to get all children room of user 
   rooms=user.room_set.all()
   # to get all messages of user
   room_messages=user.message_set.all().order_by('-created')

   topics=Topic.objects.all()
   context={'user':user, 'rooms':rooms,'room_messages':room_messages,'topics':topics}
   return render(request,"base/profile.html",context)





# -------------------------------------------------------------------------
# for creation of  room
 
@login_required(login_url='login')
def createRoom(request):  # sourcery skip: use-named-expression
   form=RoomForm()
   # to present topics dynamically
   topic_list=Topic.objects.all()
   if request.method == 'POST':
      new_topic=request.POST.get('topic_name')
   
      if new_topic:
      #  creating new topic  through get_ro_create method 
         topic,created=Topic.objects.get_or_create(name=new_topic)

         Room.objects.create(
            host=request.user,
            # adding topic form topic 
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),


         ) 
         return redirect('/')
      
   context={'form':form,'topic_list':topic_list}
   return render(request,"base/room_form.html",context)

# -------------------------------------------------------------------------
# to update room data

@login_required(login_url='login')
def updateRoom(request,pk):  # sourcery skip: use-named-expression
   # geting data from the room through id 
   room = Room.objects.get(id=pk)
   # putting data into the RoomForm
   form=RoomForm(instance=room)
    # to present topics dynamically 
   topic_list=Topic.objects.all()

   # saving from unauthenticated user to updateRoom
   if request.user !=room.host:
      return HttpResponse("You are not allowed to update this !!")
   
   # seving data after editing
   if request.method =='POST':

      new_topic=request.POST.get('topic_name')
   
      if new_topic:
      #  creating new topic  through get_ro_create method 
         topic,created=Topic.objects.get_or_create(name=new_topic)
         room.name=request.POST.get('name')
         room.topic=topic
         room.description=request.POST.get('description')
         room.save()
         return redirect("Home")


   context={'form':form,'topic_list':topic_list,'room':room}
   return render(request,"base/room_form.html",context)



# ---------------------------------------------------------------
# to delete a room

@login_required(login_url='login')
def deleteRoom(request,pk):
   room = Room.objects.get(id=pk)
    # saving from unauthenticated user to deleteRoom
   if request.user !=room.host:
      return HttpResponse("You are not allowed to delete this !!")
   if request.method =='POST': 
      room.delete()
      return redirect('Home')
   return render(request,"base/delete.html",{'obj':room})



# ---------------------------------------------------------------
# to delete a message

@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)
    if request.user !=message.user:
      return HttpResponse("You are not allowed to delete this !!")
    if request.method =='POST': 
      message.delete()
      return redirect('Home')
    return render(request,"base/delete.html",{'obj':message})




 

# ------------------------------------
# update user profile
@login_required(login_url='login')
def updateUser(request):
   user=request.user
   form = UserForm(instance=user)

   if request.method == 'POST':
      form = UserForm(request.POST,request.FILES,instance=user)
      if form.is_valid():
         form.save()
         redirect('user-profile',pk=user.id)




   return render(request,"base/update-user.html",{'form':form})



 

# for topiecs page

def topicPage(request):
   # to filer the topic
   q=request.GET.get('q') if request.GET.get('q')!=None else ''

   topics=Topic.objects.filter(name__icontains=q)
   return render(request,"base/topics.html",{'topics':topics})



# for activity page
def activityPage(request):
   room_messages=Message.objects.all()
   return render(request,"base/activity_component.html",{'room_messages':room_messages})

