from django.urls import reverse
from django.views.generic import ListView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from .models import (
    Shelf,
    SiteUser,
    ShopOwnership,
    Basket,
    Order,
    Shop,
    Product,
)

from .forms import (
    UserRegisterForm,
    AddShopForm,
    AddShelfForm,
    AddProductForm,
    AddOwnerForm,
)

# Create your views here.
# class HomeView(ListView):
#     """Home page"""
#     template_name = 'market/home.html'
#     context_object_name = 'shelves'

#     def get_queryset(self):
#         """Return the list of shelves."""
#         return Shelf.objects.order_by('-last_edit')

def HomeView(request):
    shelves = Shelf.objects.order_by('-last_edit')
    context = {'shelves': shelves}
    return render(request,'market/home.html',context)

def LoginView(request):
    context = {}
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request,email=email,password=password)
        if user:
            login(request, user)
            return redirect(to=reverse('market:home'))
    return render(request,'market/login.html',context)

def RegisterView(request):
    form = UserRegisterForm()
    context = {'form': form,}
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        context = {"form": form,}
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password1']
            user = form.save()
            authenticate(request,email=email,password=password)
            login(request,user)
            return redirect(to=reverse('market:home'))
    return render(request, 'market/register.html',context)

def LogoutView(request):
    logout(request)
    return redirect(reverse('market:login'))

def AddShopView(request):
    form = AddShopForm()
    context = {'form': form}
    if request.method == 'POST':
        form = AddShopForm(request.POST)
        context = {"form": form,}
        if form.is_valid():
            user = request.user
            shop = form.save()
            ShopOwnership.objects.create(
                owner=user,
                shop=shop,
                is_founder=True,
                can_edit_shop=True,
                can_open_shelf=True,
                can_edit_shelf=True,
                can_delete_shelf=True,
                can_add_product=True,
            )
            return redirect(to=reverse('market:my_shops'))
    return render(request,'market/add_shop.html',context)

def view_shop(request, shop_id):
    user = request.user
    try:
        _view_shop = Shop.objects.get(id=shop_id)
        perm = ShopOwnership.objects.get(shop_id=shop_id, owner=user)
        owns = ShopOwnership.objects.filter(shop_id=shop_id)
    except (Shop.DoesNotExist, ShopOwnership.DoesNotExist):
        _view_shop = None
        perm = None
        owns = []
    if not perm or not _view_shop:
        return redirect(reverse('market:my_shops'))
    shelves = Shelf.objects.filter(shop_id=shop_id)
    context = {
        'perm': perm,
        'shop': _view_shop,
        'owns': owns,
        'shelves': shelves,
    }
    return render(request, 'market/view_shop.html', context)

def edit_shop(request, shop_id):
    user = request.user
    try:
        _edit_shop = Shop.objects.get(id=shop_id)
        perm = ShopOwnership.objects.get(shop=_edit_shop, owner=user).can_edit_shop
    except (Shop.DoesNotExist, ShopOwnership.DoesNotExist):
        _edit_shop = None
        perm = False
    if not perm or not _edit_shop:
        return redirect(reverse('market:my_shops'))
    data = {
        'email': _edit_shop.email,
        'name': _edit_shop.name,
        'description': _edit_shop.description,
        'logo': _edit_shop.logo,
    }
    form = AddShopForm(data)
    context = {'form': form, 'shop': _edit_shop}
    if request.method == 'POST':
        form = AddShopForm(request.POST, initial=data, instance=_edit_shop)
        context['form'] = form
        if form.is_valid():
            form.save()
            return redirect(to=reverse('market:my_shops'))
    return render(request,'market/edit_shop.html',context)

def delete_shop(request, shop_id):
    user = request.user
    try:
        _delete_shop = Shop.objects.get(id=shop_id)
        perm = ShopOwnership.objects.get(shop=_delete_shop, owner=user).can_edit_shop
    except (Shop.DoesNotExist, ShopOwnership.DoesNotExist):
        _delete_shop = None
        perm = False
    if not perm or not _delete_shop:
        return redirect(to=reverse('market:my_shops'))
    if request.method == 'POST':
        _delete_shop.delete()
        return redirect(to=reverse('market:my_shops'))
    context = {'shop': _delete_shop}
    return render(request,'market/delete_shop.html',context)


def MyAccount(request):
    user = request.user
    if not user.is_authenticated:
        return redirect(to=reverse('market:login'))
    baskets = Basket.objects.filter(user=user, submitted=True)
    active_basket = Basket.objects.get_or_create(user=user, submitted=False)[0]
    context = {
        'user': user,
        'baskets': baskets,
        'active_basket': active_basket
    }
    return render(request,'market/my_account.html',context)

def MyBasket(request):
    user = request.user
    session = request.session
    if user.is_authenticated:
        basket = Basket.objects.get_or_create(user=user, submitted=False)[0]
    else:
        basket = Basket.objects.get_or_create(session=session, submitted=False)[0]
    orders = Order.objects.filter(basket=basket)
    context = {'user': user, 'basket': basket, 'orders': orders}
    if request.method =='POST':
        return redirect(reverse('market:dummy_payment'))
    return render(request,'market/my_basket.html',context)

def DummyPayment(request):
    user = request.user
    session = request.session
    if user.is_authenticated:
        basket = Basket.objects.get_or_create(user=user, submitted=False)[0]
    else:
        basket = Basket.objects.get_or_create(session=session, submitted=False)[0]
    context = {'user': user, 'basket': basket}
    if request.method == 'POST':
        basket.submitted = True
        basket.save()
        return redirect(reverse('market:my_basket'))
    return render(request,'market/dummy_payment.html',context)

def MyShops(request):
    user = request.user
    owns = ShopOwnership.objects.filter(owner=user)
    context = {
        'user': user ,
        'owns': owns,
    }
    return render(request, 'market/my_shops.html', context)

def add_shelf(request, shop_id):
    user = request.user
    try:
        shop = Shop.objects.get(id=shop_id, owners__id=user.id)
    except Shop.DoesNotExist:
        return render(request, 'market/add_shelf_no_shop.html')
    ownership = ShopOwnership.objects.get(shop=shop, owner=user)
    if not ownership.can_open_shelf:
        return render(request, 'market/add_shelf_no_shop.html')
    form = AddShelfForm()
    products = Product.objects.exclude(shop__id=shop.id)
    context = {
        'shop': shop,
        'form': form,
        'products': products,
    }
    if request.method == 'POST':
        form = AddShelfForm(request.POST)
        context['form']= form
        if form.is_valid():
            shelf = form.save()
            return redirect(reverse('market:shelf', kwargs={'id': shelf.id}),context)
    return render(request, 'market/add_shelf.html', context)

def add_owner(request, shop_id):
    user = request.user
    try:
        shop = Shop.objects.get(id=shop_id, owners__id=user.id)
    except Shop.DoesNotExist:
        return render(request, 'market/add_shelf_no_shop.html')
    ownership = ShopOwnership.objects.get(shop=shop, owner=user)
    if not ownership.can_edit_shop:
        return render(request, 'market/add_shelf_no_shop.html')
    form = AddOwnerForm()
    users = SiteUser.objects.exclude(shop__id=shop.id)
    context = {
        'shop': shop,
        'form': form,
        'users': users,
    }
    if request.method == 'POST':
        form = AddOwnerForm(request.POST)
        context['form']= form
        if form.is_valid():
            print('form is valid')
            form.save()
            return redirect(reverse('market:my_shops'),context)
    return render(request, 'market/add_owner.html', context)

def edit_owner(request, ownership_id):
    user = request.user
    try:
        _edit_owner = ShopOwnership.objects.get(id=ownership_id)
        perm = ShopOwnership.objects.get(shop=_edit_owner.shop, owner=user).can_edit_shop
    except ShopOwnership.DoesNotExist:
        _edit_owner = None
        perm = False
    if not perm or not _edit_owner:
        return render(request, 'market/add_shelf_no_shop.html')
    form = AddOwnerForm(instance=_edit_owner)
    context = {
        'shop': _edit_owner.shop,
        'form': form,
        'owner': _edit_owner.owner,
    }
    if request.method == 'POST':
        form = AddOwnerForm(request.POST, instance=_edit_owner)
        context['form']= form
        if form.is_valid():
            form.save()
            return redirect(reverse('market:my_shops'),context)
    return render(request, 'market/edit_owner.html', context)

def edit_shelf(request, shelf_id):
    user = request.user
    try:
        shelf = Shelf.objects.get(id=shelf_id)
        perm = ShopOwnership.objects.get(shop=shelf.shop, owner=user).can_edit_shelf
    except Shelf.DoesNotExist:
        shelf = None
        perm = False
    if not perm or not shelf:
        return render(request, 'market/edit_shelf_no_shelf.html')
    _data = {
        'shop': shelf.shop,
        'product': shelf.product,
        'price': shelf.price,
        'discount_price': shelf.discount_price,
        'remaining': shelf.remaining,
    }
    form = AddShelfForm(_data)
    context = {'form': form, 'shelf': shelf}
    if request.method == 'POST':
        _data['price'] = request.POST['price']
        if request.POST['discount_price'] == '':
            _data['discount_price'] = None
        else:
            _data['discount_price'] = request.POST['discount_price']
        _data['remaining'] = request.POST['remaining']
        form = AddShelfForm(_data)
        context['form']= form
        if form.is_valid():
            if 'price' in request.POST:shelf.price = _data['price']
            if 'discount_price' in request.POST:shelf.discount_price = _data['discount_price']
            if 'remaining' in request.POST:shelf.remaining = _data['remaining']
            shelf.save()
            return redirect(reverse('market:shelf', kwargs={'id': shelf.id}),context)
    return render(request, 'market/edit_shelf.html', context)

def delete_shelf(request, shelf_id):
    user = request.user
    try:
        shelf = Shelf.objects.get(id=shelf_id)
        perm = ShopOwnership.objects.get(shop=shelf.shop, owner=user).can_delete_shelf
    except Shelf.DoesNotExist:
        shelf = None
        perm = False
    if not perm or not shelf:
        return render(request, 'market/edit_shelf_no_shelf.html')
    context = {'shelf': shelf}
    if request.method == 'POST':
            shelf.delete()
            return redirect(reverse('market:my_shops'))
    return render(request, 'market/delete_shelf.html', context)

def delete_owner(request, ownership_id):
    user = request.user
    try:
        _delete_owner = ShopOwnership.objects.get(id=ownership_id)
        perm = ShopOwnership.objects.get(shop=_delete_owner.shop, owner=user).can_edit_shop
    except (Shelf.DoesNotExist,ShopOwnership.DoesNotExist):
        _delete_owner = None
        perm = False
    if not perm or not _delete_owner:
        return render(request, 'market/edit_shelf_no_shelf.html')
    context = {
        'shop': _delete_owner.shop,
        'owner': _delete_owner.owner,
        'own': _delete_owner,
    }
    if request.method == 'POST':
            _delete_owner.delete()
            return redirect(reverse('market:my_shops'))
    return render(request, 'market/delete_shelf.html', context)

def add_product(request):
    user = request.user
    owns = ShopOwnership.objects.filter(owner=user)
    perm = False
    for own in owns:
        if own.can_add_product:
            perm = True
            break
    if not perm:
        return redirect(reverse('market:my_shops'))
    form = AddProductForm()
    context = {'form': form}
    if request.method == 'POST':
        _post = {'registerd': 'on'}
        if 'name' in request.POST: _post['name'] = request.POST['name']
        if 'description' in request.POST: _post['description'] = request.POST['description']
        form = AddProductForm(_post)
        context = {'form': form}
        if form.is_valid():
            form.save()
            return redirect(reverse('market:home'))
    return render(request, 'market/add_product.html', context)

def ShelfDetail(request, id):
    _shelf = Shelf.objects.get(id=id)
    context = {'shelf': _shelf}
    if request.method == 'POST':
        user = request.user
        number = request.POST['number']
        _basket = Basket.objects.get_or_create(user=user, submitted=False)[0]
        _order, new_order = Order.objects.get_or_create(
            shelf=_shelf, basket=_basket,
            defaults={'number': number}
        )
        if not new_order:
            _order.number += number
            _order.save
        return redirect(reverse('market:home'))
    return render(request, 'market/shelf_details.html', context)
