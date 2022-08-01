from email.policy import default
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.contrib.sessions.models import Session
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy as n_


def shop_images(instance, filename):
    """Return file name and path to save the ``Shop``s logo image."""
    return f'shop_{instance.name}_{filename}'

def profile_images(instance, filename):
    """Return file name and path to save the ``SiteUser``s profile image"""
    return f'user_{instance.name}_{filename}'

class Product(models.Model):
    """Product model
    General characteristics of a product that shops can offer.
    """
    name = models.CharField(
        max_length=256,
        verbose_name=_('product name'),
    )
    description = models.TextField(
        verbose_name=_('description'),
    )
    registerd = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name}'

class Shop(models.Model):
    """Shop model
    Contact and descriptions of a shop which a ``SitUser`` has made.
    """
    name = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name=_('shop name'),
    )
    description = models.TextField(
        verbose_name=_('description'),
        null=True,
        blank=True,
    )
    email = models.EmailField(
        verbose_name=_('email address'),
        unique=True,
    )
    logo = models.ImageField(
        upload_to=shop_images,
        null=True,
        blank=True,
        verbose_name=_('logo'),
        default='default_shop_logo.png'
    )
    owners = models.ManyToManyField(
        to='SiteUser',
        verbose_name=_('owners'),
        through='ShopOwnership',
        related_name='shops',
        related_query_name="shop",
    )
    shelves = models.ManyToManyField(
        to='Product',
        verbose_name=_('products'),
        through='Shelf',
        related_name='shops',
        related_query_name="shop",
    )
    opening_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}'

class ShopOwnership(models.Model):
    """Shop Ownership model
    A many-to-many relation between ``SiteUser`` and ``Shop``.
    Containing permissions for shop actions.
    """
    owner = models.ForeignKey('SiteUser', on_delete=models.CASCADE)
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE)
    # Permissions
    is_founder = models.BooleanField(default=False, verbose_name=_("founder"))
    can_edit_shop = models.BooleanField(default=False, verbose_name=_("edit shop"))
    can_open_shelf = models.BooleanField(default=False, verbose_name=_("open shelf"))
    can_edit_shelf = models.BooleanField(default=False, verbose_name=_("edit shelf"))
    can_delete_shelf = models.BooleanField(default=False, verbose_name=_("delete shelf"))
    can_add_product = models.BooleanField(default=False, verbose_name=_("product registration request"))

    class Meta:
        constraints = [
            models.UniqueConstraint('shop', 'owner', name='unique_shop_owner'),
        ]

    def __str__(self):
        return f'{self.owner} owns {self.shop}'

class Shelf(models.Model):
    """Shelf model
    A many-to-many relation between ``Shop`` and ``Product``.
    Containing the normal and optional discout price the Shop
    offers for the Product, number of Products they have to sell, etc.
    """
    product = models.ForeignKey('Product', on_delete=models.CASCADE,verbose_name=_('product'))
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE,verbose_name=_('shop'))
    price = models.PositiveBigIntegerField(verbose_name=_('price'))
    discount_price = models.PositiveBigIntegerField(
        blank=True,
        null=True,
        verbose_name='dicount price'
    )
    remaining = models.PositiveBigIntegerField(verbose_name=_('remaining'))
    opening_date = models.DateTimeField(auto_now_add=True, verbose_name=_('opening date'))
    last_edit = models.DateTimeField(auto_now=True, verbose_name=_('last edit'))

    def __str__(self) -> str:
        return f'{self.product}-{self.price}'
    @property
    def final_price(self):
        if self.discount_price:
            return self.discount_price
        else:
            return self.price

class Basket(models.Model):
    """Basket model
    A collection of ``Order`` to be ordered(bought) by a ``SiteUser``.
    """
    user = models.ForeignKey('SiteUser', on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('user'))
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True)
    orders = models.ManyToManyField(
        to='Shelf',
        verbose_name=_('orders'),
        through='Order',
        related_name='orders',
        related_query_name="order",
    )
    submitted = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user',],condition=Q(submitted=False), name='user_not_submitted_unique'),
            models.UniqueConstraint(fields=['session',],condition=Q(submitted=False), name='session_not_submitted_unique'),
        ]
    
    def __str__(self) -> str:
        if self.user:
            if self.submitted:
                return f'{self.user} {self.total_price()} ' + _('submitted')
            else:
                return f'{self.user} {self.total_price()} ' + _('active')
        else:
            if self.submitted:
                return _('anonymus') + f' {self.total_price()} ' + _('submitted')
            else:
                return _('anonymus') + f' {self.total_price()} ' + _('active')

    def total_price(self):
        self_orders = Order.objects.filter(basket=self)
        price = 0
        for order in self_orders:
            price += order.total_price()
        return price

class Order(models.Model):
    """Order model
    A many-to-many relation between ``Shelf`` and ``Basket``.
    Containing number of ordered ``Product`` from the ``Shelf``,
    and applying a constraint to avoid having two separate order
    from the same shelf. It should be a single order with an
    incremented number.
    """
    shelf = models.ForeignKey('Shelf', on_delete=models.CASCADE)
    basket = models.ForeignKey('Basket', on_delete=models.CASCADE)
    number = models.PositiveBigIntegerField(verbose_name=_('number of products'))

    class Meta:
        constraints = [
            models.UniqueConstraint('shelf', 'basket', name='unique_shelf_basket')
        ]
    
    def __str__(self) -> str:
        return n_('%(num)d %(product)s','%(num)d %(product)ss', 'num') % {'num': self.number, 'product': self.shelf.product}

    def total_price(self):
        return self.shelf.final_price * self.number

class SiteUserManager(BaseUserManager):
    """A custom manager for ``SiteUser``."""
    def create_user(
        self,
        email,
        username,
        first_name=None,
        last_name=None,
        profile=None,
        password=None,
        **kwargs,
    ):
        """
        Creates and saves a User with the given name
        email, profile, and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            profile=profile,
            **kwargs,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email,
        username,
        first_name=None,
        last_name=None,
        profile=None,
        password=None,
        **kwargs,
    ):
        """
        Creates and saves a superuser with the given name,
        email, profile, and password.
        """
        user = self.create_user(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            profile=profile,
            password=password,
            **kwargs,
        )
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class SiteUser(AbstractBaseUser):
    """A custom user class with a profile picture.
    """
    email = models.EmailField(
        verbose_name=_('email'),
        max_length=255,
        unique=True,
    )
    username = models.CharField(
        max_length=64,
        verbose_name=_('username'),
    )
    first_name = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name=_('first name'),
    )
    last_name = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name=_('last name'),
    )
    profile = models.ImageField(
        upload_to=profile_images,
        null=True,
        blank=True,
        verbose_name=_('profile'),
        default='default.png',
    )

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = SiteUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return '{0}'.format(self.username)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
