from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
     name=models.CharField(max_length=200,null=True)
     email=models.EmailField(unique=True,null=True)
     bio=models.TextField(null=True)

    #  avatar
     avatar=models.ImageField(null=True,default="avatar.svg")
    # 
     USERNAME_FIELD='email'
     REQUIRED_FIELDS=[]


 



# ----
class Topic(models.Model):
    name=models.CharField(max_length=200)

    def __str__(self):
        return self.name

# createing models for room
class Room(models.Model):
    host=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    # if the class topic is somewhere in down wthen use 'Topic'
    topic=models.ForeignKey(Topic,on_delete=models.SET_NULL,null=True)
    name=models.CharField(max_length=200)
    description=models.TextField(null=True, blank=True)

    participants=models.ManyToManyField(User , related_name='participants', blank=True)
    updated=models.DateTimeField(auto_now=True)
    created=models.DateTimeField(auto_now_add=True)
    # add new things to top
    class Meta:
        ordering =['-updated', '-created']


    def __str__(self):
        return self.name
    


# to send messages into rooms

class Message(models.Model):
   user=models.ForeignKey(User,on_delete=models.CASCADE)
   room= models.ForeignKey(Room,on_delete=models.CASCADE)
   body= models.TextField(max_length=1000)
   update=models.DateTimeField(auto_now=True)
   created=models.DateTimeField(auto_now_add=True)

#    class Meta:
#         ordering =['-updated', '-created']

   def __str__(self) :
      return self.body[:50]