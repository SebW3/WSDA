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

        age_rating = request.POST.getlist("age_rating")
        age_condition = Q()
        for age in age_rating:
            if age == "Little kids":
                age_condition |= Q(rating="G")
                age_condition |= Q(rating="TV-Y")
                age_condition |= Q(rating="TV-G")
            if age == "Older kids":
                age_condition |= Q(rating="PG")
                age_condition |= Q(rating="TV-Y7")
                age_condition |= Q(rating="TV-Y7-FV")
                age_condition |= Q(rating="TV-PG")
            if age == "Teens":
                age_condition |= Q(rating="PG-13")
                age_condition |= Q(rating="TV-14")
            if age == "Mature":
                age_condition |= Q(rating="R")
                age_condition |= Q(rating="NC-17")
                age_condition |= Q(rating="TV-MA")

            query &= Q(age_condition)

        if len(query) == 0:  # if no filters = return blank page
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