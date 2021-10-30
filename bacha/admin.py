from django.contrib import admin
from .models import Profile, Product, Transaction, Job, Comment, Review

# Register your models here.
admin.site.register([Product, Profile, Transaction, Job, Comment, Review])