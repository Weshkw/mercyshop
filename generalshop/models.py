from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from datetime import datetime
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator



class CustomUserManager(BaseUserManager):
    def create_user(self, id_number, first_name, middle_name, surname, phone_number, password):
        """
        Creates and saves a CustomUser with the given id_number, first name, middle name,
        surname, phone number, and password.
        """
        if not id_number:
            raise ValueError('Please ensure you enter your ID number.')
        
        if not first_name:
            raise ValueError('Please ensure you enter your first name.')
        
        if not middle_name:
            raise ValueError('Please ensure you enter your middle name.')
        
        if not surname:
            raise ValueError('Please ensure you enter your surname.')
        
        if not  phone_number:
            raise ValueError('Please ensure you enter your  phone number.')
        
        

        user = self.model(
            id_number=id_number,
            first_name=first_name,
            middle_name=middle_name,
            surname=surname,
            phone_number=phone_number,
        )

        user.set_password(raw_password = password)
        user.save(using=self._db)
        return user

    def create_superuser(self,  id_number, first_name, middle_name, surname, phone_number, password):
        """
        Creates and saves a superuser with the given id_number, first name, middle name,
        surname, phone number, and password.
        """
        user = self.create_user(
            id_number=id_number,
            first_name=first_name,
            middle_name=middle_name,
            surname=surname,
            phone_number=phone_number,
            password=password,
        )

        user.is_staff = True
        user.is_superuser = True
        user.is_admin = True
        user.save(using=self._db)
        return user



class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Define the fields for the custom user model
    first_name = models.CharField(max_length=30, verbose_name='First name')
    middle_name = models.CharField(max_length=30, verbose_name='Middle name')
    surname = models.CharField(max_length=30, verbose_name='Surname')
    id_number = models.CharField(max_length=30, unique=True)
    phone_number = models.CharField(max_length=15)

    # Define additional fields required by Django
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser= models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # Use the custom manager for the custom user model
    objects = CustomUserManager()

    # Define the username field for the custom user model
    REQUIRED_FIELDS = ['first_name', 'middle_name', 'surname', 'phone_number']
    USERNAME_FIELD = 'id_number'
    

    

    # Define methods to return the full and short names of the user
    def __str__(self):
        return self.first_name + ' ' + self.middle_name

    def get_full_name(self):
        return self.first_name + ' ' + self.middle_name + ' ' + self.surname

    def get_short_name(self):
        return self.first_name






class InventoryProducts(models.Model):
    product_name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    home_image = models.ImageField()
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_amount = models.IntegerField()
    unit_type = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name
    
class MoreImages(models.Model):
    name = models.ForeignKey(InventoryProducts, on_delete=models.CASCADE, related_name='moreimages')
    more_images = models.FileField()


    
class FeaturedVideo(models.Model):
    
    video = models.FileField()






class PettyCosts(models.Model):
    employee = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    activity = models.CharField(max_length=200)
    transport_cost = models.DecimalField(max_digits=6, decimal_places=2, blank=True)
    lunch_cost = models.DecimalField(max_digits=6, decimal_places=2,blank=True)
    airtime_cost = models.DecimalField(max_digits=6, decimal_places=2,blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    

    def __str__(self):
        return self.activity
    
class OtherPettyCosts(models.Model):
    pettycosts= models.ForeignKey(PettyCosts, on_delete=models.CASCADE)
    employee = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    others=models.CharField(max_length=200, blank=True, null=True)
    expense=models.DecimalField(max_digits=6, decimal_places=2,blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    

class Order(models.Model):
    transaction_id=models.CharField(max_length=200)
    complete=models.BooleanField(default=False,null=True,blank=True)
    date_ordered= models.DateTimeField(auto_now_add=True)

    @property
    def get_order_total(self):
        order_items = self.ordered_products.all()
        total = sum(item.get_total for item in order_items)
        return total
        
    @property
    def get_order_quantity(self):
        order_items = self.ordered_products.all()
        quantity = sum(item.quantity for item in order_items)
        return quantity

    def __str__(self):
        return str(self.id)

class OrderedProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True, related_name='ordered_products')
    product = models.ForeignKey(InventoryProducts, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True, validators=[MinValueValidator(1)])
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.selling_price * self.quantity
        return total







