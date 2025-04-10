from rest_framework import serializers
from .models import Book,User,Seller,Order,Review,Request
from django.contrib.auth.hashers import make_password


class BookSerializer(serializers.ModelSerializer):
    seller = serializers.PrimaryKeyRelatedField(queryset=Seller.objects.all())  # ✅ Should reference Seller, not User
    image = serializers.ImageField(required=False)  

    class Meta:
        model = Book
        fields = ['book_id', 'seller', 'title', 'author', 'category', 'price', 'availability_status', 
                  'rental_option', 'condition', 'quantity', 'image']

    def create(self, validated_data):
        """
        If a book with the same title, author, and seller exists, 
        increase the quantity instead of creating a duplicate.
        """
        seller = validated_data.get('seller')  # ✅ Use 'seller' instead of 'seller_id'
        title = validated_data.get('title')
        author = validated_data.get('author')
        
        # Check if a book with the same seller, title, and author exists
        existing_book = Book.objects.filter(seller=seller, title=title, author=author).first()

        if existing_book:
            existing_book.quantity += validated_data.get('quantity', 1)  # ✅ Increase quantity
            existing_book.save()
            return existing_book  # ✅ Return the updated book instance

        return super().create(validated_data)  # ✅ Otherwise, create a new book entry

        
class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True)  # Ensure password is write-only

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name','password']
        
    def update(self, instance, validated_data):
        # If password is being updated, hash it
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).update(instance, validated_data)
    
    def create(self, validated_data):
        """Hash the password before saving"""
        password = validated_data.pop('password')  # Remove password from data
        user = User(**validated_data)  # Create user instance
        user.set_password(password)  # Hash password
        user.save()
        return user


class SellerSerializer(serializers.Serializer):
    seller_id = serializers.IntegerField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    shop_name = serializers.CharField(max_length=255)
    gstin = serializers.CharField(max_length=15)

    approved_status = serializers.BooleanField(default=False)
    
    def validate(self, data):
        """Ensure GSTIN is unique"""
        if Seller.objects.filter(gstin=data['gstin']).exists():
            raise serializers.ValidationError({"gstin": "A seller with this GSTIN already exists."})
        return data
    
    def create(self, validated_data):
        """Manually create a Seller object"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['user'] = request.user  # Assign the logged-in user
        return Seller.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Manually update a Seller object"""
        instance.shop_name = validated_data.get('shop_name', instance.shop_name)
        instance.approved_status = validated_data.get('approved_status', instance.approved_status)
        instance.save()
        return instance



class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_id', 'user', 'book', 'order_date', 'total_amount', 'status']
        read_only_fields = ['order_id', 'order_date']  # These fields should not be modified manually

    def validate_total_amount(self, value):
        """Ensure total_amount is a positive value"""
        if value <= 0:
            raise serializers.ValidationError("Total amount must be greater than zero.")
        return value



class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['review_id', 'user', 'book', 'rating', 'comment', 'review_date']
        read_only_fields = ['review_id', 'review_date']  # Prevents modification of these fields

    def validate_rating(self, value):
        """Ensure rating is between 1 and 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['request_id', 'user', 'book_title', 'author', 'status']
        read_only_fields = ['request_id']  # Ensure ID is not required for input

    def validate_status(self, value):
        """Ensure that the status is valid before updating."""
        if value not in ['pending', 'fulfilled', 'rejected']:
            raise serializers.ValidationError("Invalid status. Choose from: pending, fulfilled, or rejected.")
        return value