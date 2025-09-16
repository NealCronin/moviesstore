from django.contrib import admin

# Register your models here.
from .models import Order
from movies.models import Movie
admin.site.register(Order)