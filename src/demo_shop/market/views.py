from django.urls import reverse
from django.views.generic import ListView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.sessions.models import Session

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
    UserEditForm,
    AddShopForm,
    EditShopForm,
    AddShelfForm,
    EditShelfForm,
    AddProductForm,
    AddOwnerForm,
    EditOwnerForm,
    OrderForm,
    LoginForm,
)

def home_view(request):
    shelves = Shelf.objects.order_by('-last_edit')
    context = {'shelves': shelves}
    return render(request,'market/home.html',context)

def login_view(request):
    form = LoginForm()
    print('session_key: ',request.session.session_key)
    anonymous_basket = Basket.objects.get_or_create(session_id=request.session.session_key, submitted=False)[0]
    context = {'form': form}
    if request.method == 'POST':
        form = LoginForm(request.POST)
        context['form'] = form
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request,email=email,password=password)
            if user:
                login(request, user)
                user_basket = Basket.objects.get_or_create(user=user, submitted=False)[0]
                return redirect(reverse('market:resolve_baskets', kwargs={'anonymous_basket_id': anonymous_basket.pk, 'user_basket_id': user_basket.pk}))
            form.add_error(None, 'ایمیل و رمز همخوانی ندارد')
            form.add_error(None, 'به فارسی و انگلیسی بودن اعداد رمز دقت کنید')
    return render(request,'market/login.html',context)

def resolve_baskets_view(request, anonymous_basket_id, user_basket_id):
    try:
        user_basket = Basket.objects.get(pk=user_basket_id)
        anonymous_basket = Basket.objects.get(pk=anonymous_basket_id)
    except Basket.DoesNotExist:
        return redirect(to=reverse('market:home'))

    user_orders = list(Order.objects.filter(basket=user_basket))
    anonymous_orders = list(Order.objects.filter(basket=anonymous_basket))

    conflict_counter = 0
    conflicts = {'anonymous_orders':[],'user_orders':[]}
    for user_order in user_orders:
        for anonymous_order in anonymous_orders:
            if user_order.shelf == anonymous_order.shelf:
                conflict_counter += 1
                conflicts['anonymous_orders'].append(anonymous_order)
                conflicts['user_orders'].append(user_order)
    
    context = {
        'user_orders': conflicts['user_orders'],
        'anonymous_orders': conflicts['anonymous_orders'],
    }
    # moving non-conflicting orders to users basket
    for order in conflicts['anonymous_orders']:
        anonymous_orders.remove(order)
    for order in anonymous_orders:
        order.basket = user_basket
    
    if not conflict_counter:
        Order.objects.bulk_update(user_orders,fields=['basket','number'])
        Basket.objects.filter(user=None, session=None).delete()
        return redirect(reverse('market:home'))
    if request.method == 'POST':
        print(f"action: {request.POST.get('action')}")
        if request.POST.get('action') == 'add':
            for index in range(conflict_counter):
                conflicts['user_orders'][index].number += conflicts['anonymous_orders'][index].number
        elif request.POST.get('action') == 'user':
            pass
        elif request.POST.get('action') == 'anonymous':
            for index in range(conflict_counter):
                conflicts['user_orders'][index].number = conflicts['anonymous_orders'][index].number
        else:
            return render(request,'market/resolve_baskets.html',context)
        Order.objects.bulk_update(user_orders,fields=['basket','number'])
        Basket.objects.filter(user=None, session=None).delete()
        return redirect(reverse('market:home'))
    return render(request,'market/resolve_baskets.html',context)

def register_view(request):
    form = UserRegisterForm()
    context = {'form': form,}
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        context = {"form": form,}
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user = form.save()
            # authenticate(request,email=email,password=password)
            # login(request,user)
            return redirect(to=reverse('market:login'))
    return render(request, 'market/register.html',context)

def logout_view(request):
    logout(request)
    request.session.create()
    return redirect(reverse('market:login'))

def add_shop_view(request):
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
        shop = Shop.objects.get(id=shop_id)
        perm = ShopOwnership.objects.get(shop=shop, owner=user).can_edit_shop
    except (Shop.DoesNotExist, ShopOwnership.DoesNotExist):
        shop = None
        perm = False
    if not perm or not shop:
        return redirect(reverse('market:my_shops'))
    form = EditShopForm(instance=shop)
    context = {'form': form, 'shop': shop}
    if request.method == 'POST':
        form = EditShopForm(request.POST,instance=shop)
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

@login_required(login_url='/login/')
def my_account(request):
    user = request.user
    baskets = Basket.objects.filter(user=user, submitted=True)
    active_orders = Order.objects.filter(basket__user=user, basket__submitted=False)
    context = {
        'user': user,
        'baskets': baskets,
        'active_orders': active_orders,
    }
    return render(request,'market/my_account.html',context)

@login_required(login_url='/login/')
def edit_account(request):
    user = request.user
    form = UserEditForm(instance=user)
    context = {'user': user, 'form': form}
    return render(request, 'market/edit_account.html', context)

def my_basket(request):
    user = request.user
    session = Session.objects.get(pk=request.session.session_key)
    if user.is_authenticated:
        basket = Basket.objects.get_or_create(user=user, submitted=False)[0]
    else:
        basket = Basket.objects.get_or_create(session=session, submitted=False)[0]
    orders = Order.objects.filter(basket=basket)
    context = {'user': user, 'basket': basket, 'orders': orders}
    if request.method =='POST':
        return redirect(reverse('market:dummy_payment'))
    return render(request,'market/my_basket.html',context)

@login_required(login_url='/login/')
def dummy_payment(request):
    user = request.user
    session = Session.objects.get(session_key=request.session.session_key)
    if user.is_authenticated:
        basket = Basket.objects.get_or_create(user=user, submitted=False)[0]
    else:
        basket = Basket.objects.get_or_create(session=session, submitted=False)[0]
    context = {'user': user, 'basket': basket}
    if request.method == 'POST':
        basket.submitted = True
        basket.save()
        return redirect(reverse('market:my_account'))
    return render(request,'market/dummy_payment.html',context)

@login_required(login_url='/login/')
def my_shops(request):
    user = request.user
    # if not user.is_authenticated:
    #     return redirect(reverse('market:home'))
    owns = ShopOwnership.objects.filter(owner=user)
    context = {
        'user': user ,
        'owns': owns,
    }
    return render(request, 'market/my_shops.html', context)

@login_required(login_url='/login/')
def add_shelf(request, shop_id):
    user = request.user
    try:
        shop = Shop.objects.get(id=shop_id, owners__id=user.id)
    except Shop.DoesNotExist:
        return render(request, 'market/add_shelf_no_shop.html')
    ownership = ShopOwnership.objects.get(shop=shop, owner=user)
    if not ownership.can_open_shelf:
        return render(request, 'market/add_shelf_no_shop.html')
    form = AddShelfForm(initial={'shop': shop})
    products = Product.objects.exclude(shop__id=shop.id)
    context = {
        'shop': shop,
        'form': form,
        'products': products,
    }
    if request.method == 'POST':
        form = AddShelfForm(request.POST, initial={'shop': shop})
        context['form']= form
        if form.is_valid():
            shelf = form.save()
            return redirect(reverse('market:shelf', kwargs={'id': shelf.id}),context)
    return render(request, 'market/add_shelf.html', context)

@login_required(login_url='/login/')
def add_owner(request, shop_id):
    user = request.user
    try:
        shop = Shop.objects.get(id=shop_id, owners__id=user.id)
    except Shop.DoesNotExist:
        return render(request, 'market/add_shelf_no_shop.html')
    ownership = ShopOwnership.objects.get(shop=shop, owner=user)
    if not ownership.can_edit_shop:
        return render(request, 'market/add_shelf_no_shop.html')
    form = AddOwnerForm(initial={"shop": shop})
    users = SiteUser.objects.exclude(shop__id=shop.id)
    context = {
        'shop': shop,
        'form': form,
        'users': users,
    }
    if request.method == 'POST':
        form = AddOwnerForm(request.POST, initial={"shop": shop})
        context['form']= form
        if form.is_valid():
            print('form is valid')
            form.save()
            return redirect(reverse('market:my_shops'),context)
    return render(request, 'market/add_owner.html', context)

@login_required(login_url='/login/')
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
    form = EditOwnerForm(instance=_edit_owner)
    for w in form:print(w.value)
    context = {
        'shop': _edit_owner.shop,
        'form': form,
        'owner': _edit_owner.owner,
    }
    if request.method == 'POST':
        form = EditOwnerForm(request.POST, instance=_edit_owner)
        context['form']= form
        print('in post')
        if form.is_valid():
            form.save()
            return redirect(reverse('market:my_shops'),context)
    return render(request, 'market/edit_owner.html', context)

@login_required(login_url='/login/')
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
    form = EditShelfForm(instance=shelf)
    context = {'form': form, 'shelf': shelf}
    if request.method == 'POST':
        form = EditShelfForm(request.POST, instance=shelf)
        context['form']= form
        if form.is_valid():
            form.save()
            return redirect(reverse('market:shelf', kwargs={'id': shelf.id}),context)
    return render(request, 'market/edit_shelf.html', context)

@login_required(login_url='/login/')
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

@login_required(login_url='/login/')
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
    return render(request, 'market/delete_owner.html', context)

@login_required(login_url='/login/')
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

def shelf_detail(request, id):
    shelf = Shelf.objects.get(id=id)
    form = OrderForm({'number': 1})
    context = {'shelf': shelf, 'form': form}
    if request.method == 'POST':
        user = request.user
        session = Session.objects.get(session_key=request.session.session_key)
        if user.is_authenticated:
            basket = Basket.objects.get_or_create(user=user, submitted=False)[0]
        else:
            basket = Basket.objects.get_or_create(session=session)[0]
            print(session)
        order, new_order = Order.objects.get_or_create(
            shelf=shelf, basket=basket,
            defaults={'number': 0}
        )
        form = OrderForm(request.POST, instance=order)
        context['form'] = form
        if form.is_valid():
            if form.cleaned_data.get('number') > shelf.remaining:
                form.add_error('number','we dont have that much')
                context['form'] = form
                order.delete()
                return render(request, 'market/shelf_details.html', context)
            if new_order:
                form.save()
            else:
                order.number += form.cleaned_data.get('number')
                order.save()
            shelf.remaining -= form.cleaned_data.get('number')
            shelf.save()
            return redirect(reverse('market:home'))
    return render(request, 'market/shelf_details.html', context)
