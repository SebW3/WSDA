from django.shortcuts import render
from django.db.models import Q
from .models import Entry

# Create your views here.
def home(request):
    return render(request, "home.html", {"result" : "Your results will be shown here"})

def search_result(request):
    if request.method == "POST":
        query = Q()

        type1 = request.POST.getlist("type1")
        if len(type1) == 1:
            query &= Q(type1=type1[0])


        searched = request.POST["searched"]
        if len(searched.strip()) > 0:
            query &= Q(title__contains=searched)


        genres = request.POST.getlist("genres")
        for genre in genres:
            query &= Q(listed_in__contains=genre)


        if len(searched) == 0 and len(type1) == 0 and len(genres) == 0:  # if no filters = return blank page
            return render(request, "search_result.html")

        # run query
        result = Entry.objects.filter(query)
        query = result.query

        if len(result) == 0:
            result = ["No content with these filters"]

        test = [searched, type1, genres]

        return render(request, "search_result.html", {"searched" : searched, "result" : result, "test" : test, "query" : query, "request_POST" : request.POST})
    else:
        return render(request, "search_result.html")