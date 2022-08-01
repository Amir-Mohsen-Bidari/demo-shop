from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .widgets import (
    MyImageInput,
    MyCheckboxInput,
    MySelectInput,
)
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
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': _('Enter your password')}))
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput(attrs={'placeholder': _('Repeat your password')}))
    email = forms.EmailField(max_length=255,widget=forms.EmailInput(attrs=({'placeholder':_('Enter your email'), 'dir': 'auto'})))
    username = forms.CharField(max_length=64,widget=forms.TextInput(attrs=({'placeholder':_('Username'), 'dir': 'auto'})))
    first_name = forms.CharField(max_length=64,required=False, widget=forms.TextInput(attrs=({'placeholder':_('Fisrt name'), 'dir': 'auto'})))
    last_name = forms.CharField(max_length=64,required=False, widget=forms.TextInput(attrs=({'placeholder':_('Last name'), 'dir': 'auto'})))
    profile = forms.ImageField(required=False, widget=MyImageInput)

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
            raise ValidationError(_("Passwords don't match"))
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserEditForm(forms.ModelForm):
    """A form for editing users. Includes all the required
    fields, plus a repeated password."""
    username = forms.CharField(max_length=64,required=False,widget=forms.TextInput(attrs=({'placeholder':_('Username'), 'dir': 'auto'})))
    first_name = forms.CharField(max_length=64,required=False, widget=forms.TextInput(attrs=({'placeholder':_('First name'), 'dir': 'auto'})))
    last_name = forms.CharField(max_length=64,required=False, widget=forms.TextInput(attrs=({'placeholder':_('Last name'), 'dir': 'auto'})))
    profile = forms.ImageField(required=False, widget=MyImageInput)

    class Meta:
        model = SiteUser
        fields = (
            'username',
            'first_name',
            'last_name',
            'profile',
        )

class LoginForm(forms.Form):
    email = forms.EmailField(label='email', max_length=255,widget=forms.EmailInput(attrs=({'placeholder':_('Enter your email'), 'dir': 'auto'})))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': _('Enter your password')}))

class AddShopForm(forms.ModelForm):
    """A form for creating new shops."""
    email = forms.EmailField(widget=forms.EmailInput(attrs=({'placeholder':_("Enter your shop's email"), 'dir': 'auto'})))
    name = forms.CharField(max_length=64, widget=forms.TextInput(attrs=({'placeholder':_("Enter your shop's name"), 'dir': 'auto'})))
    description = forms.CharField(widget=forms.Textarea(attrs=({'placeholder':_("A brief desciption of your shop"), 'dir': 'auto', 'cols': '30', 'rows': '5'})))
    logo = forms.ImageField(required=False, widget=MyImageInput)

    class Meta:
        model = Shop
        fields = (
            'email',
            'name',
            'description',
            'logo',
        )

class EditShopForm(forms.ModelForm):
    """A form for editing shops."""
    name = forms.CharField(max_length=64, widget=forms.TextInput(attrs=({'placeholder':_("Enter your shop's name"), 'dir': 'auto'})))
    description = forms.CharField(widget=forms.Textarea(attrs=({'placeholder':_("A brief desciption about your shop"), 'dir': 'auto', 'cols': '30', 'rows': '5'})))
    logo = forms.ImageField(required=False, widget=MyImageInput)

    class Meta:
        model = Shop
        fields = (
            'name',
            'description',
            'logo',
        )

class AddShelfForm(forms.ModelForm):
    """A form for creating new shelfs."""
    shop = forms.ModelChoiceField(disabled=True, queryset=Shop.objects)
    product = forms.ModelChoiceField(queryset=Product.objects, widget=MySelectInput)
    price = forms.IntegerField(min_value=0,max_value=9223372036854775807,widget=forms.NumberInput(attrs=({'placeholder': _("Price")})))
    discount_price = forms.IntegerField(min_value=0,max_value=9223372036854775807,required=False,widget=forms.NumberInput(attrs=({'placeholder': _("Discount price (not necessary)")})))
    remaining = forms.IntegerField(min_value=0,max_value=9223372036854775807,widget=forms.NumberInput(attrs=({'placeholder': _("Remaining (we don't sell more than this number)")})))

    class Meta:
        model = Shelf
        fields = (
            'shop',
            'product',
            'price',
            'discount_price',
            'remaining',
        )
    
    def clean_product(self):
        product = self.cleaned_data.get('product')
        shop = self.initial.get('shop')
        active_shelves = Product.objects.filter(shop=shop)
        if product in active_shelves:
            raise ValidationError(_('Already have a shelf for this product'))
        return product
    
    def clean_shop(self):
        shop = self.get_initial_for_field(self.fields['shop'],'shop')
        if shop not in Shop.objects.all():
            raise ValidationError(_('No such shop'))
        return shop

class EditShelfForm(forms.ModelForm):
    """A form for editing shelfs."""
    price = forms.IntegerField(min_value=0,max_value=9223372036854775807,widget=forms.NumberInput(attrs=({'placeholder': _("Price")})))
    discount_price = forms.IntegerField(min_value=0,max_value=9223372036854775807,required=False,widget=forms.NumberInput(attrs=({'placeholder': _("Discount price (not necessary)")})))
    remaining = forms.IntegerField(min_value=0,max_value=9223372036854775807,widget=forms.NumberInput(attrs=({'placeholder': _("Remaining (we don't sell more than this number)")})))

    class Meta:
        model = Shelf
        fields = (
            'price',
            'discount_price',
            'remaining',
        )

class AddProductForm(forms.ModelForm):
    """A form for creating new shelfs."""
    name = forms.CharField(max_length=64, widget=forms.TextInput(attrs=({'placeholder':_("Product's name"), 'dir': 'auto'})))
    description = forms.CharField(widget=forms.Textarea(attrs=({'placeholder':_("A brief description about product"), 'dir': 'auto', 'cols': '30', 'rows': '5'})))
    class Meta:
        model = Product
        fields = (
            'name',
            'description',
        )

class AddOwnerForm(forms.ModelForm):
    """A form for creating new shop ownerships."""
    shop = forms.ModelChoiceField(disabled=True, queryset=Shop.objects)
    owner = forms.ModelChoiceField(queryset=SiteUser.objects, widget=MySelectInput)
    can_edit_shop = forms.BooleanField(required=False,widget=MyCheckboxInput(text=_("Edit Shop")))
    can_open_shelf = forms.BooleanField(required=False,widget=MyCheckboxInput(text=_("Add Shelf")))
    can_edit_shelf = forms.BooleanField(required=False,widget=MyCheckboxInput(text=_("Edit Shelf")))
    can_delete_shelf = forms.BooleanField(required=False,widget=MyCheckboxInput(text=_("Delete Shelf")))
    can_add_product = forms.BooleanField(required=False,widget=MyCheckboxInput(text=_("Product Registration Request")))
    class Meta:
        model = ShopOwnership
        fields = (
            'shop',
            'owner',
            'can_edit_shop',
            'can_open_shelf',
            'can_edit_shelf',
            'can_delete_shelf',
            'can_add_product',
        )

    def clean_shop(self):
        shop = self.get_initial_for_field(self.fields['shop'],'shop')
        if shop not in Shop.objects.all():
            raise ValidationError('No such shop')
        return shop

    def clean_owner(self):
        owner = self.cleaned_data.get('owner')
        shop = self.cleaned_data.get('shop')
        if owner in SiteUser.objects.filter(shop=shop):
            raise ValidationError(_('Already owns this shop'))
        return owner

class EditOwnerForm(forms.ModelForm):
    """A form for editing shop ownerships."""
    can_edit_shop = forms.BooleanField(required=False,widget=MyCheckboxInput(text=_("Edit Shop")))
    can_open_shelf = forms.BooleanField(required=False,widget=MyCheckboxInput(text=_("Add Shelf")))
    can_edit_shelf = forms.BooleanField(required=False,widget=MyCheckboxInput(text=_("Edit Shelf")))
    can_delete_shelf = forms.BooleanField(required=False,widget=MyCheckboxInput(text=_("Delete Shelf")))
    can_add_product = forms.BooleanField(required=False,widget=MyCheckboxInput(text=_("Product Registration Request")))
    class Meta:
        model = ShopOwnership
        fields = (
            'can_edit_shop',
            'can_open_shelf',
            'can_edit_shelf',
            'can_delete_shelf',
            'can_add_product',
        )

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('number',)
