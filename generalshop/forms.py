from decimal import Decimal

from django import forms
from django.db import transaction

from .models import FeaturedVideo, InventoryProducts, MoreImages, OtherPettyCosts, PettyCosts


class MultipleImageInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    """An image field that accepts several files and cleans to a list."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleImageInput(attrs={"accept": "image/*"}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        files = data if isinstance(data, list | tuple) else [data]
        return [super(MultipleImageField, self).clean(file, initial) for file in files if file]


class ProductForm(forms.ModelForm):
    gallery = MultipleImageField(label="More images", required=False)

    class Meta:
        model = InventoryProducts
        fields = [
            "product_name",
            "description",
            "home_image",
            "buying_price",
            "selling_price",
            "unit_amount",
            "unit_type",
        ]
        labels = {"home_image": "Main image"}

    @transaction.atomic
    def save(self):
        product = super().save()
        for image in self.cleaned_data["gallery"]:
            MoreImages.objects.create(name=product, more_images=image)
        return product


class FeaturedVideoForm(forms.ModelForm):
    class Meta:
        model = FeaturedVideo
        fields = ["video"]


class PettyCostsForm(forms.ModelForm):
    others = forms.CharField(label="Other cost", max_length=200, required=False)
    expense = forms.DecimalField(
        label="Other cost amount", max_digits=6, decimal_places=2, min_value=0, required=False
    )

    class Meta:
        model = PettyCosts
        fields = ["activity", "transport_cost", "lunch_cost", "airtime_cost"]

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("expense") and not cleaned_data.get("others"):
            self.add_error("others", "Describe what the other cost was for.")
        return cleaned_data

    @transaction.atomic
    def save_for(self, employee):
        petty_costs = super().save(commit=False)
        petty_costs.employee = employee
        petty_costs.save()
        if self.cleaned_data["others"]:
            OtherPettyCosts.objects.create(
                pettycosts=petty_costs,
                others=self.cleaned_data["others"],
                expense=self.cleaned_data["expense"] or Decimal(0),
            )
        return petty_costs
