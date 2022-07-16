from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from .models import (
    SiteUser,
    Shop,
    Product,
    ShopOwnership,
    Shelf,
    Basket,
    Order,
)

class UserRegisterForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = SiteUser
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'profile',
        )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class AddShopForm(forms.ModelForm):
    """A form for creating new shops."""
    class Meta:
        model = Shop
        fields = (
            'email',
            'name',
            'description',
            'logo',
        )

class AddShelfForm(forms.ModelForm):
    """A form for creating new shelfs."""
    class Meta:
        model = Shelf
        fields = (
            'shop',
            'product',
            'price',
            'discount_price',
            'remaining',
        )

class AddProductForm(forms.ModelForm):
    """A form for creating new shelfs."""
    class Meta:
        model = Product
        fields = (
            'name',
            'description',
            'registerd',
        )

class AddOwnerForm(forms.ModelForm):
    """A form for creating new shelfs."""
    class Meta:
        model = ShopOwnership
        fields = (
            'owner',
            'shop',
            'can_edit_shop',
            'can_open_shelf',
            'can_edit_shelf',
            'can_delete_shelf',
            'can_add_product',
        )
