from django import views
from django.urls import path
from .views import (
    HomeView,
    LoginView,
    RegisterView,
    LogoutView,
    AddShopView,
    MyAccount,
    MyBasket,
    MyShops,
    add_shelf,
    edit_shelf,
    delete_shelf,
    add_product,
    ShelfDetail,
    DummyPayment,
    add_owner,
    edit_owner,
    delete_owner,
    edit_shop,
    view_shop,
    delete_shop,
)

app_name = 'market'

urlpatterns = [
    path('', HomeView, name='home'),
    path('login/', LoginView, name='login'),
    path('logout/', LogoutView, name='logout'),
    path('register/', RegisterView, name='register'),# Add user
    path('add_shop/', AddShopView, name='add_shop'),
    path('my_account/', MyAccount, name='my_account'),
    path('my_basket/', MyBasket, name='my_basket'),
    path('my_shops/', MyShops, name='my_shops'),
    path('shop/<int:shop_id>', view_shop, name='shop'),
    path('edit_shop/<int:shop_id>', edit_shop, name='edit_shop'),
    path('delete_shop/<int:shop_id>', delete_shop, name='delete_shop'),
    path('add_shelf/<int:shop_id>', add_shelf, name='add_shelf'),
    path('edit_shelf/<int:shelf_id>', edit_shelf, name='edit_shelf'),
    path('delete_shelf/<int:shelf_id>', delete_shelf, name='delete_shelf'),
    path('add_owner/<int:shop_id>', add_owner, name='add_owner'),
    path('edit_owner/<int:ownership_id>', edit_owner, name='edit_owner'),
    path('delete_owner/<int:ownership_id>', delete_owner, name='delete_owner'),
    path('add_product', add_product, name='add_product'),
    path('shelf/<int:id>/', ShelfDetail, name='shelf'),
    path('dummy_payment/', DummyPayment, name='dummy_payment'),
]
