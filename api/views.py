from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from rest_framework import viewsets,permissions
from api.models import Book,User,Seller,Order,Review,Request
from api.serializers import BookSerializer,UserSerializer,SellerSerializer,OrderSerializer,ReviewSerializer,RequestSerializer
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    AllowAny
)

from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model


from rest_framework import status   
# Create your views here.
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    
class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes=[IsAdminUser]
    
class RegisterUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def get_permissions(self):
        """Define permissions based on action"""
        if self.action == 'create':  
            return [AllowAny()]  # Allow anyone to register
        return [IsAdminUser()]  # Only admin can view all users
    
class SellerViewSet(viewsets.ModelViewSet):
    serializer_class = SellerSerializer
    permission_classes = [IsAuthenticated]  # Only logged-in users can access
    queryset = Seller.objects.all()

    def perform_create(self, serializer):
        """Assign the logged-in user to the seller"""
        serializer.save(user=self.request.user)
        
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Custom endpoint to update order status"""
        try:
            order = self.get_object()
            new_status = request.data.get("status")

            if new_status not in ['pending', 'shipped', 'delivered', 'cancelled']:
                return Response({"error": "Invalid status value."}, status=status.HTTP_400_BAD_REQUEST)

            order.status = new_status
            order.save()
            return Response({"message": "Status updated successfully.", "order": OrderSerializer(order).data})
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
    def perform_create(self, serializer):
        """Automatically assign the logged-in user to the order"""
        serializer.save(user=self.request.user)
        
class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows reviews to be viewed, created, updated, and deleted.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Allow only authenticated users to create reviews

    def perform_create(self, serializer):
        """Ensure the review is associated with the currently logged-in user."""
        serializer.save(user=self.request.user)

class RequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to create, update, view, and delete book requests.
    """
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Only logged-in users can create/update/delete

    def perform_create(self, serializer):
        """Automatically assigns the request to the logged-in user."""
        serializer.save(user=self.request.user)

class CustomJWTLoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'is_seller': user.is_seller 
                
            })
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class GetSellersByUserID(APIView):
    def get(self, request, user_id):
        sellers = Seller.objects.filter(user__id=user_id)
        
        if not sellers.exists():
            return Response({"message": "No sellers found for this user."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(SellerSerializer(sellers, many=True).data, status=status.HTTP_200_OK)

User = get_user_model()

class SetSellerStatusView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ Only authenticated users can update

    def post(self, request):
        user = request.user  # Get the logged-in user
        user.is_seller = True  # Set `is_seller` to True
        user.save()  # Save the change

        return Response({"message": "User is now a seller", "is_seller": user.is_seller}, status=status.HTTP_200_OK)