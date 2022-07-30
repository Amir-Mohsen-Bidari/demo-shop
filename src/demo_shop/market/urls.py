from django import views
from django.urls import path
from .views import (
    home_view,
    login_view,
    register_view,
    logout_view,
    add_shop_view,
    my_account,
    my_basket,
    my_shops,
    add_shelf,
    edit_shelf,
    delete_shelf,
    add_product,
    shelf_detail,
    dummy_payment,
    add_owner,
    edit_owner,
    delete_owner,
    edit_shop,
    view_shop,
    delete_shop,
    resolve_baskets_view,
    edit_account,
)

app_name = 'market'

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('resolve_baskets/<int:anonymous_basket_id>-<int:user_basket_id>/', resolve_baskets_view, name='resolve_baskets'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),# Add user
    path('add_shop/', add_shop_view, name='add_shop'),
    path('my_account/', my_account, name='my_account'),
    path('my_basket/', my_basket, name='my_basket'),
    path('my_shops/', my_shops, name='my_shops'),
    path('shop/<int:shop_id>/', view_shop, name='shop'),
    path('edit_shop/<int:shop_id>/', edit_shop, name='edit_shop'),
    path('delete_shop/<int:shop_id>/', delete_shop, name='delete_shop'),
    path('add_shelf/<int:shop_id>/', add_shelf, name='add_shelf'),
    path('edit_shelf/<int:shelf_id>/', edit_shelf, name='edit_shelf'),
    path('delete_shelf/<int:shelf_id>/', delete_shelf, name='delete_shelf'),
    path('add_owner/<int:shop_id>/', add_owner, name='add_owner'),
    path('edit_owner/<int:ownership_id>/', edit_owner, name='edit_owner'),
    path('delete_owner/<int:ownership_id>/', delete_owner, name='delete_owner'),
    path('add_product/', add_product, name='add_product'),
    path('shelf/<int:id>/', shelf_detail, name='shelf'),
    path('dummy_payment/', dummy_payment, name='dummy_payment'),
    path('edit_account/', edit_account, name='edit_account')
]
