from django.db import models

# Create your models here.
class Entry(models.Model):
    type1 = models.CharField(max_length=8)
    title = models.TextField()
    director = models.TextField()
    cast = models.TextField()
    country = models.TextField()
    date_added = models.DateField()
    release_year = models.IntegerField()
    rating = models.CharField(max_length=8)
    duration = models.CharField(max_length=10)
    listed_in = models.TextField()
    description = models.TextField()

    class Meta:
        db_table = "content"

    def __str__(self):
        return self.title
