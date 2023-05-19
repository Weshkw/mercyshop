# Import necessary modules
from django import forms
from django.forms.widgets import ClearableFileInput, MultiWidget, FileInput
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser,InventoryProducts
from django import forms
from .models import PettyCosts, OtherPettyCosts




# Create a new `UserRegistrationForm` class that inherits from Django's built-in `UserCreationForm` class and includes the custom fields
class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    middle_name = forms.CharField(max_length=30)
    surname = forms.CharField(max_length=30)
    id_number = forms.CharField(max_length=30, required=True, help_text='Required. Must be a unique value')
    phone_number = forms.CharField(max_length=15)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'middle_name', 'surname', 'id_number', 'phone_number', 'password1', 'password2')



class PettyCostsForm(forms.ModelForm):
    class Meta:
        model = PettyCosts
        fields = ['activity', 'transport_cost', 'lunch_cost', 'airtime_cost']
        
    others = forms.CharField(max_length=200, required=False)
    expense = forms.DecimalField(max_digits=6, decimal_places=2, required=False)
           




    




