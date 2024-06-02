from django.shortcuts import render
from .models import Entry

# Create your views here.
def home(request):
    # from django.db import reset_queries, connection
    # reset_queries()

    # result = Entry.objects.filter(id=2)
    # test = Entry.objects.filter(id=2).query
    result = None
    test = None

    return render(request, "home.html", {"result" : result, "test" : test})

def search_result(request):
    if request.method == "POST":
        test = None
        if "TV show" in request.POST and "Movie" in request.POST:
            type1 = None
        elif "TV show" in request.POST:
            type1 = "TV show"
        elif "Movie" in request.POST:
            type1 = "Movie"
        else:
            type1 = None
            if len(request.POST["searched"].strip()) == 0:
                return render(request, "search_result.html")
            test = str(request.POST)

        searched = request.POST["searched"]

        if type1 and searched:
            result = Entry.objects.filter(title__contains=searched, type1=type1)
        elif type1:
            result = Entry.objects.filter(type1=type1)
        else:
            result = Entry.objects.filter(title__contains=searched)

        query = result.query

        return render(request, "search_result.html", {"searched" : searched, "result" : result, "test" : test, "query" : query})
    else:
        return render(request, "search_result.html")