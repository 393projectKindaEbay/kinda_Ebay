from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home_view(request, *args, **kwargs):
    print(request.user)
    return render(request, "home.html",{})

def about_view(request, *args, **kwargs):
    return render(request, "about.html",{})

def commodities_view(request, *args, **kwargs):
    my_context = {
        "my_text"   :   "this is about us",
        "my_number" :   123,
        "my_list"   :   [123,456,789,"abc"]
    }
    return render(request, "commodities.html",my_context)