from django.contrib import admin
from django.urls import path,include
from api.views import BookViewSet,UsersViewSet,RegisterUserViewSet,SellerViewSet,OrderViewSet,ReviewViewSet,RequestViewSet,GetSellersByUserID,SetSellerStatusView
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"books",BookViewSet)
router.register(r"users",UsersViewSet)
router.register(r'register', RegisterUserViewSet, basename='register')
router.register(r'seller', SellerViewSet, basename='seller')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'reviews', ReviewViewSet)
router.register(r'request', RequestViewSet)




urlpatterns = [
    path("",include(router.urls)),
    path("sellers/<int:user_id>/", GetSellersByUserID.as_view(), name="get_sellers_by_user"),
    path("set-seller/", SetSellerStatusView.as_view(), name="set_seller"),


       
]