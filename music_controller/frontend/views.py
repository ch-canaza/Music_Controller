from django.shortcuts import render

# Create your views here.

def index(request, *args, **kwargs):
    """ 
        render index html file from front end 
    """
    return render(request, 'frontend/index.html')
