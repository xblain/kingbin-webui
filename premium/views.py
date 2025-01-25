from django.shortcuts import render
from django.http import HttpRequest

# Create your views here.
def premium(request: HttpRequest):
    return render(request, "premium.html")