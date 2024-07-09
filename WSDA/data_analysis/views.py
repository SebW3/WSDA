from django.shortcuts import render
from django.db.models import Q
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import io
import urllib, base64
import plotly.figure_factory as ff
import plotly.graph_objs as go
import plotly
import json
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

            # if only one type selected
            if request.POST["Movie length"] and request.POST.getlist("type1")[0] == "Movie":
                length = request.POST["Movie length"]
                if len(length) == 1:
                    query &= Q(duration__regex=f'^[0123456789] ')
                else:
                    query &= Q(duration__regex=f'^{length[:-1]}[0123456789] ') | Q(duration__regex=f'^{str(int(length)-10)[:-1]}[0123456789] ')

            if request.POST["Number of seasons"] and request.POST.getlist("type1")[0] == "TV show":
                number = request.POST["Number of seasons"]
                query &= Q(duration__regex=f'^{number} .eason*')

        elif len(type1) == 2:
            length = request.POST["Movie length"]
            number = request.POST["Number of seasons"]
            if len(length) == 1:
                query &= (Q(duration__regex=f'^[0123456789] ') & Q(type1="Movie")) | (Q(duration__regex=f'^{number} .eason*') & Q(type1="TV Show"))
            elif len(length) == 0:
                query &= (Q(duration__regex=f'^{length[:-1]}[0123456789] ') & Q(type1="Movie")) | (Q(duration__regex=f'^{number} .eason*') & Q(type1="TV Show"))
            else:
                query &= (Q(duration__regex=f'^{length[:-1]}[0123456789] ') & Q(type1="Movie")) | (Q(duration__regex=f'^{str(int(length) - 10)[:-1]}[0123456789] ') & Q(type1="TV Show")) | (Q(duration__regex=f'^{number} .eason*') & Q(type1="TV Show"))


        searched = request.POST["searched"]
        if len(searched.strip()) > 0:
            query &= Q(title__contains=searched)


        genres = request.POST.getlist("genres")
        for genre in genres:
            query &= Q(listed_in__contains=genre)

        age_rating = request.POST.getlist("age_rating")
        if age_rating:
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

        release_year = request.POST.getlist("release_year")
        if release_year:
            release_year_condition = Q()
            for year in release_year:
                release_year_condition |= Q(release_year=f'{year}')

            query &= Q(release_year_condition)

        countries = request.POST.getlist("countries")
        if countries:
            countries_condition = Q()
            for country in countries:
                countries_condition |= Q(country=f'{country}')

            query &= Q(countries_condition)


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

def graphs(request):
    test = None
    df = pd.read_csv("../netflix_titles.csv")
    df.drop(columns=["show_id"], inplace=True)

    type_counts = df['type'].value_counts()

    # Prepare data for Chart.js pie chart
    pie_labels = type_counts.index.tolist()
    pie_data = type_counts.values.tolist()
    pie_colors = ['#000000', '#fd0000'] + ['#%06x' % (i * 0x111111) for i in range(len(type_counts) - 2)]  # Extend colors if needed

    # Calculate percentages for pie chart
    total = sum(pie_data)
    percentages = [(count / total) * 100 for count in pie_data]

    # Get the top 10 countries with the most content for bar chart
    country_counts = df['country'].value_counts().head(10)
    bar_labels = country_counts.index.tolist()
    bar_data = country_counts.values.tolist()
    bar_colors = ['#fd0000'] + ['#%06x' % (i * 0x111111) for i in range(len(country_counts) - 1)]

    # Prepare data for horizontal bar chart
    genre_counts = df['listed_in'].str.split(', ', expand=True).stack().value_counts().head(10)
    hbar_labels = genre_counts.index.tolist()
    hbar_data = genre_counts.values.tolist()
    hbar_colors = ['#df0000'] + ['#%06x' % (i * 0x111111) for i in range(len(genre_counts) - 1)]

    # Prepare data for the distribution plot
    movies = df[df['type'] == 'Movie'].copy()
    movies['duration'] = movies['duration'].str.replace(' min', '')
    movies_duration = movies['duration'].astype(float).dropna()
    x = movies_duration.values
    hist_data = [x]

    fig = ff.create_distplot(hist_data, ['Duration'], show_rug=False)
    mean_value = movies_duration.mean()
    fig.add_trace(go.Scatter(
        x=[mean_value, mean_value],
        y=[0, 0.025],
        mode="lines",
        name="Mean",
        line=dict(color="red", width=2, dash="dash")
    ))

    fig.update_layout(
        width=900,
        height=600,
        paper_bgcolor='#2c2c2c',
        plot_bgcolor='#2c2c2c',
        font=dict(color='white'),
        showlegend=True,
        xaxis=dict(title='Duration (minutes)', titlefont=dict(size=14, color='white'), tickfont=dict(color='white')),
        margin=dict(l=0, r=0, t=40, b=40)
    )

    distplot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # world map
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3])

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)



    return render(request, "graphs.html", {"test" : test,
            "pie_labels": pie_labels,
            "percentages": percentages,
            "pie_colors": pie_colors,
            "bar_labels": bar_labels,
           "bar_data": bar_data,
           "bar_colors": bar_colors,
           "hbar_labels": hbar_labels,
           "hbar_data": hbar_data,
           "hbar_colors": hbar_colors,
           "distplot_json": distplot_json,
           "world_map": uri
        })