from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

def validate_positive(value):
    if value <= 0:
        raise ValidationError(
            _('%(value)s is not a positive number not equal to 0'),
            params={'value': value},
        )
# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    balance = models.SmallIntegerField(verbose_name='Bank Balance', default=10)

    username = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return " ".join([self.first_name, self.last_name])

class Comment(models.Model):
    commenter = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="commenter")
    comment = models.TextField(verbose_name='Comment',max_length=2000)
    time = models.DateTimeField(auto_now_add=True, verbose_name='Comment Time')
    def __str__(self):
        return self.comment

class Review(models.Model):
    choices = [
        (1, "1 - Really Bad"),
        (2, "2 - Bad"),
        (3, "3 - Ok"),
        (4, "4 - Good"),
        (5, "5 - Really Good")
    ]
    stars = models.SmallIntegerField(verbose_name="Star Rating", choices=choices)
    commenter = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="reviewer")
    comment = models.TextField(verbose_name='Comment', max_length=2000)
    def __str__(self):
        return " ".join([str(self.stars), self.comment])

class Transaction(models.Model):
    payer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="payer") # The Foreign key to the Profiles involved
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="receiver")

    description = models.TextField(verbose_name='Message to receiver',max_length=2000)
    amount = models.SmallIntegerField(verbose_name='Amount', validators=[validate_positive])

    time = models.DateTimeField(auto_now_add=True, verbose_name='Time of Transaction', blank=True)

    choices = (
        (True, 'Read'),
        (False, 'Unread')
    )
    read = models.BooleanField(default=False, verbose_name="Read By Receiver", choices=choices)
    
    def __str__(self):
        return self.description

class Product(models.Model):
    seller = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="seller") # The Foreign key to the Profiles involved
    buyers = models.ManyToManyField(Profile, related_name="buyers")

    transactions = models.ManyToManyField(Transaction)

    # Some of the Product's attributes
    name = models.CharField(verbose_name='Product Name', max_length=50)
    description = models.TextField(verbose_name='Product Description',max_length=2000)
    price = models.PositiveSmallIntegerField(verbose_name='Price')
    availability = models.SmallIntegerField(verbose_name="Amount of Products", validators=[validate_positive])
    reviews = models.ManyToManyField(Review)
    def __str__(self):
        return self.name

class Job(models.Model):
    employer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="employer")

    name = models.CharField(verbose_name='Work Name', max_length=50)
    description = models.TextField(verbose_name='Work Description',max_length=2000)
    pay = models.PositiveSmallIntegerField(verbose_name='Pay')
    minutes = models.PositiveSmallIntegerField(verbose_name='Physical Minutes')
    BOOL_CHOICES = ((True, 'Public'), (False, 'Private'))
    availability = models.BooleanField(verbose_name="Job Avalability", choices=BOOL_CHOICES) # True if Public False if Private
    
    transactions = models.ManyToManyField(Transaction)

    workers = models.ManyToManyField(Profile)
    comments = models.ManyToManyField(Comment)

    def __str__(self):
        return self.name
