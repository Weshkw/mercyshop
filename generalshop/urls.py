from django.urls import path
from . import views




urlpatterns = [
    path('',views.homepage, name='home' ),


   # path('register/',views.register, name='register'),
    
    path('moreinfo/<int:pk>/',views.moreinfo, name='moreinfo'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('searchproduct/', views.search, name='searchproduct'),
    path('createproduct/', views.create_product, name='createproduct'),
    path('pettycosts/', views.petty_costs, name='pettycosts'),
    path('addvideo/', views.addvideo, name='addvideo'),

    path('cart/', views.cart, name='cart'),
    path('addtocart/', views.add_to_cart, name='addtocart'),
    path('increasequantity/', views.increaseQuantityOfCartProduct, name='increaseQuantityOfCartProduct'),
    path('decreasequantity/', views.decreaseQuantityOfCartProduct, name='decreaseQuantityOfCartProduct'),
    path('deletecartitem/', views.deleteCartItem, name='deletecartitem'),

 
]
