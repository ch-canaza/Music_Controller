from django.db import models
import string
import random


def generate_unique_code():
    """ method that creates a random code:
            # generates a random code of lenght 6 in uppercase
            # if code does not exist in DB create it
    """

    lenght = 6

    while True:
        
        code = ''.join(random.choices(string.ascii_uppercase, k=lenght))
        
        if Room.objects.filter(code=code).count == 0:
            break
        return code


# Create your models here.
class Room(models.Model):
    """
        clas that defines all fields in a model with unique codes
    """
    code = models.CharField(max_length=8, default=generate_unique_code, unique=True)
    host = models.CharField(max_length=50, unique=True)
    guest_can_pause = models.BooleanField(null=False, default=False)
    votes_to_skip = models.IntegerField(null=False, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
