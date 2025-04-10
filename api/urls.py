from django.contrib import admin
from django.urls import path,include
from api.views import BookViewSet,UsersViewSet,RegisterUserViewSet,SellerViewSet,OrderViewSet,ReviewViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"books",BookViewSet)
router.register(r"users",UsersViewSet)
router.register(r'register', RegisterUserViewSet, basename='register')
router.register(r'seller', SellerViewSet, basename='seller')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'reviews', ReviewViewSet)



urlpatterns = [
    path("",include(router.urls))
]