from django.urls import path
from .views import DeleteWishlistItem

urlpatterns = [
    path('wishlist/<str:product_id>/', DeleteWishlistItem.as_view(), name='delete_wishlist_item'),
]
