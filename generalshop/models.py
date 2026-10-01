from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

VIDEO_EXTENSIONS = ["mp4", "webm", "ogg"]


class CustomUserManager(BaseUserManager):
    def create_user(self, id_number, password=None, **extra_fields):
        if not id_number:
            raise ValueError("An ID number is required.")
        user = self.model(id_number=id_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, id_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(id_number, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """A shop employee who signs in with their national ID number."""

    first_name = models.CharField("first name", max_length=30)
    middle_name = models.CharField("middle name", max_length=30)
    surname = models.CharField(max_length=30)
    id_number = models.CharField("ID number", max_length=30, unique=True)
    phone_number = models.CharField(max_length=15)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "id_number"
    REQUIRED_FIELDS = ["first_name", "middle_name", "surname", "phone_number"]

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return " ".join(filter(None, [self.first_name, self.middle_name, self.surname]))

    def get_short_name(self):
        return self.first_name


class InventoryProducts(models.Model):
    product_name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    home_image = models.ImageField(upload_to="products/")
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_amount = models.PositiveIntegerField()
    unit_type = models.CharField(max_length=50)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_created"]
        verbose_name = "product"

    def __str__(self):
        return self.product_name


class MoreImages(models.Model):
    """An extra photo shown in a product's gallery."""

    name = models.ForeignKey(InventoryProducts, on_delete=models.CASCADE, related_name="moreimages")
    more_images = models.ImageField(upload_to="products/gallery/")

    class Meta:
        verbose_name = "gallery image"

    def __str__(self):
        return f"Gallery image for {self.name}"


class FeaturedVideo(models.Model):
    video = models.FileField(
        upload_to="videos/", validators=[FileExtensionValidator(VIDEO_EXTENSIONS)]
    )

    class Meta:
        ordering = ["-pk"]

    def __str__(self):
        return self.video.name


class PettyCosts(models.Model):
    """Day-to-day running costs an employee spent on one activity."""

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    activity = models.CharField(max_length=200)
    transport_cost = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal(0))
    lunch_cost = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal(0))
    airtime_cost = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal(0))
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_created"]
        verbose_name_plural = "petty costs"

    def __str__(self):
        return self.activity


class OtherPettyCosts(models.Model):
    """A cost that does not fit the transport, lunch or airtime columns."""

    pettycosts = models.ForeignKey(PettyCosts, on_delete=models.CASCADE, related_name="other_costs")
    others = models.CharField("description", max_length=200, blank=True, default="")
    expense = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal(0))
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "other petty costs"

    def __str__(self):
        return self.others


class Order(models.Model):
    """A shopping cart while ``complete`` is false."""

    transaction_id = models.CharField(max_length=200, blank=True)
    complete = models.BooleanField(default=False)
    date_ordered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.pk}"

    @property
    def total(self):
        return sum((item.line_total for item in self.ordered_products.all()), Decimal(0))

    @property
    def item_count(self):
        return sum(item.quantity for item in self.ordered_products.all())


class OrderedProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="ordered_products")
    product = models.ForeignKey(InventoryProducts, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_added"]
        constraints = [
            models.UniqueConstraint(fields=["order", "product"], name="one_line_per_product"),
        ]

    def __str__(self):
        return f"{self.quantity} × {self.product}"

    @property
    def line_total(self):
        return self.product.selling_price * self.quantity
