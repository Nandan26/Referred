from django.db import models
from django.db.models.deletion import CASCADE
# for default User model
# from django.contrib.auth.models import User

#for custom user model
from django.contrib.auth.models import AbstractUser

from django.core.validators import FileExtensionValidator

class User(AbstractUser):
    name = models.CharField(max_length=150, help_text ='Enter your full name')
    
    email = models.EmailField(unique=True)

    username = models.CharField(max_length=100, unique=True)
    
    bio = models.TextField(null=True, blank=True)

    linkedin = models.URLField(unique = True,null=True, blank=True)

    avatar = models.ImageField(upload_to = 'images/', null=True, default="images/avatar.svg")

    followers = models.ManyToManyField("self", blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','name']
    
    def __str__(self):
        return str(self.name)
    

class Company(models.Model):
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name 

class Room(models.Model):
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, null=True) 
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null = True)
    position = models.CharField(max_length = 200)
    description = models.TextField()

    # The related_name attribute specifies the name of the reverse relation from the User model back to your model. 
    # If you don’t specify a related_name, Django automatically creates one using the name of your model with the suffix _set.

    # participants = models.ManyToManyField(User, related_name = 'participants' ,blank = True)
    total_applications = models.IntegerField(default=0)
    location = models.CharField(max_length=250, null=True, blank = True)

    skills = models.TextField(max_length = 150, blank=True, null= True, help_text ='Enter all the required skills each separated by commas. ex. Java, Python, Django')
    link = models.URLField(blank = True, null = True, help_text ='Link to the carrier page of company so if they want they can directly apply there')
    experience = models.CharField(max_length = 100, blank = True, null = True)
    updated = models.DateTimeField(auto_now = True) #every time we save 
    created = models.DateTimeField(auto_now_add = True) # at first time we created / instance was created

    #for ordering objects of room by created or updated value
    class Meta:
        ordering = ['-updated', '-created']
    
    def __str__(self):
        return self.position 

class Message(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now = True) #every time we save 
    created = models.DateTimeField(auto_now_add = True) # at first time we created / instance was created

    class Meta:
        ordering = ['-updated', '-created']
    
    def __str__(self):
        if len(self.body) > 60:
            return self.body[:60] + '.....'
        return self.body

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    notification_type = models.CharField(max_length = 20,choices = (('room', 'Room creation'),('selected','Selected for refferal')),default = 'room') 

    def __str__(self):
        return self.user
    
class Application(models.Model):

    applicant = models.ForeignKey(User, on_delete=models.CASCADE)

    opportunity = models.ForeignKey(Room, on_delete=models.CASCADE)

    resume  = models.FileField(upload_to = 'pdfs/', validators=[FileExtensionValidator(allowed_extensions=["pdf"])], help_text='upload pdf file only')

    applied = models.DateTimeField(auto_now_add = True)

    experience = models.CharField(max_length = 100, blank = True, null = True)

    def __str__(self):
        return self.applicant.name

class Selected(models.Model):
    
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)

    opportunity = models.ForeignKey(Room, on_delete=models.CASCADE)

    resume  = models.FileField()

    applied = models.DateTimeField()

    experience = models.CharField(max_length = 100, blank = True, null = True)

    def __str__(self):
        return self.applicant.name 
