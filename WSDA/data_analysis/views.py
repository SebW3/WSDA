from django.shortcuts import render
from .models import Entry

# Create your views here.
def home(request):
    # from django.db import reset_queries, connection
    # reset_queries()

    result = Entry.objects.filter(id=2)
    test = Entry.objects.filter(id=2).query

    return render(request, "home.html", {"result" : result, "test" : test})
