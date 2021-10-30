from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Comment, Profile, Review, Transaction, Job, Product

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

def validate_positive(value):
    if value <= 0:
        raise ValidationError(
            _('%(value)s is not a positive number'),
            params={'value': value},
        )
class JobPayForm(forms.Form):
    bonus = forms.IntegerField(required=True, label='Bonus', validators=[validate_positive])
    comment = forms.CharField(required=False, max_length=2000, label='Comment')

class profileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email']
        #The labels attribute is optional. It is used to define the labels of the form fields created   
        labels = {
                "first_name": _("First Name     "),
                "last_name": _("Last Name     "),
                "email": _("Email Address")
                }

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['receiver', 'description', 'amount']

    def clean_from_sender(self, sender, receiver):
        if sender == receiver:
            self._errors["piece"] = "Please enter a valid model"
            self.add_error('receiver', "You cannot send money to yourself")
            return False
        return True
    
"""     def __init__(self, *args, **kwargs):
        self.balance = kwargs.pop('balance', 0)
        self.user_id = kwargs.pop('user_id', 0)
        super(TransactionForm, self).__init__(*args, **kwargs) """

"""     def clean(self):
        super(TransactionForm, self).clean()
        amount = self.cleaned_data.get('amount')
        rec = self.cleaned_data.get('receiver')
        print("amount", amount)
        if amount == None:
            amount = 0

        if self.balance + 50 < amount:
            self._errors['amount'] = self.error_class([
                'You do not have enough money to pay this. Please enter a new amount'])

        if rec != None and rec.id == self.user_id:
            self._errors['receiver'] = self.error_class([
                'You can not pay yourself'])

        return self.cleaned_data

    def is_valid(self):
        super(TransactionForm, self).is_valid()
        amount = self.cleaned_data.get('amount')
        rec = self.cleaned_data.get('receiver')
        print("amount", amount)
        if amount == None:
            amount = 0
            self._errors['amount'] = self.error_class([
                'Please enter an amount'])
            return False

        if self.balance + 50 < amount:
            self._errors['amount'] = self.error_class([
                'You do not have enough money to pay this. Please enter a new amount'])
            return False

        if rec != None and rec.id == self.user_id:
            self._errors['receiver'] = self.error_class([
                'You can not pay yourself'])
            return False
        elif rec == None:
            return False

        return True """

class WithdrawForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount']

class DepositForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['name', 'description', 'pay', 'minutes', 'availability']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'availability']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['stars', 'comment']

class createUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']