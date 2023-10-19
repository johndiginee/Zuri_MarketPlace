from django.shortcuts import render
from MarketPlace.models import Product, ProductImage, ProductCategory, ProductSubCategory, SelectedCategories
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .serializers import ProductsubCatSerializer, ProductImageSerializer
from all_products.serializers import AllProductSerializer as ProductSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

# Create your views here.

# class GetCategoryNames(APIView):
#     '''This class will return the names of all the categories in the database'''

#     def get(self, request):
#         '''Return the categories'''
#         categories = ProductCategory.objects.all()
#         name = []
#         for cat in categories:
#             if cat not in name:
#                 name.append(cat.name)
#         return Response({"categories name": name}, status=status.HTTP_200_OK)



class GetImages(ListAPIView):
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        if not (product_id := self.kwargs.get('productId')):
            # Use get() method to avoid KeyError
            return ProductImage.objects.all()
        try:
            return ProductImage.objects.filter(product_id=product_id)
        except ProductImage.DoesNotExist:
            return Response(
                {"error": "ProductImage does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        



# class GetImage(APIView):
#     def get(self, request, productId):
#         try:
#             images = ProductImage.objects.get(product=productId)
#             response = {
#                     'message': 'This is the url to where the image is hosted',
#                     'url': images.url
#                 }
#             return Response(response, status=status.HTTP_200_OK)
#         except ProductImage.DoesNotExist:
#             return Response({"error": "ProductImage does not exist"})


# class subCat(ListAPIView):
#     def get(self, request, cat, Subcat):
#         page = request.GET.get('page', 1)
#         items_per_page = request.GET.get('itemsPerPAge', 10)
#         offset = (int(page) - 1) * int(items_per_page)

#         products = Product.objects.filter(is_deleted='active')
#         paginator = Paginator(products, items_per_page)
#         try:
#             try:
#                 products = paginator.page(page)
#             except PageNotAnInteger:
#                 products = paginator.page(1)
#             except EmptyPage:
#                 products = paginator.page(paginator.num_pages)
        
#             product_data = []

#             for product in products:
#                 categories = []
#                 selected_categories = product.selected_categories.all()
#                 for sel_cat in selected_categories:
#                     sub_category = sel_cat.sub_category
#                     categories.append({
#                     'id': sel_cat.product_category.id,
#                     'name': sel_cat.product_category.name,
#                     'sub_categories': {
#                         'id': sub_category.id,
#                         'name': sub_category.name,
#                         'parent_category_id': sub_category.parent_category,
#                     }
#                 })
#             promo_product = product.promo_product

#             product_data.append({
#                 'id': product.id,
#                 'category': product.category,
#                 'name': product.name,
#                 'decsription': product.name,
#                 'quantity': product.quantity,
#                 'price': product.price,
#                 'discount_price': product.discount_price,
#                 'tax': product.tax,
#                 'admin_status': product.admin_status,
#                 'is_published': product.is_published,
#                 'is_deleted': product.is_deleted,
#                 'currency': product.currency,
#                 'createdat': product.createdat,
#                 'updatedat': product.updateat,
#                 'category': categories,
#                 'promo': promo_product,
#             })

#             response_data = {
#                 'data': {
#                     'itemsPerPage': int(items_per_page),
#                     'page': int(page),
#                     'totalPages': paginator.num_pages,
#                     'totalProducts': paginator.count,
#                     'products': product_data,

#                 }
#             }

#             # catId = ProductCategory.objects.filter(name=cat)
#             # subCat = ProductSubCategory.objects.filter(name=Subcat, parent_category=catId)
#             # products = Product.objects.filter(is_deleted='active')
#             # for product in products:
#             #     selected = SelectedCategories(sub_category=subCat, product_category=catId, product=products)
#             return Response(response_data)

#         except Exception as e:
#             return Response({"error": f"Exception raised {e}"})

class GetProductsSubCategory(APIView):
    def get(self, request, category, subcategory):

        if not isinstance(category, str):
            return Response({"error": "Category name must be string"}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(subcategory, str):
            return Response({"error": "Sub category name must be string"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            try:
                category_obj = ProductCategory.objects.get(name=category)
            except ProductCategory.DoesNotExist:
                return Response({"Message": f"There is no product category named {category}"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': e})

            try:
                ProductSubCategory.objects.filter(name=subcategory, parent_category=category_obj)
                prod = Product.objects.filter(category=category_obj, is_deleted='active', admin_status='approved', is_published=True)
                
            except ProductSubCategory.DoesNotExist:
                return Response({'error': f'There is no sub category named {subcategory} under {category}'})
            except Exception as e:
                return Response({'error': e})


            if not prod.exists():
                response = {
                    "status": 200,
                    "message": "There are no products in this subcategory",
                    "data": []
                }
                return Response({"products": [], "Message": "There are no products in this subCategory"}, status=status.HTTP_200_OK)

            page = request.GET.get('page', 1)
            items_per_page = request.GET.get('itemsPerPage', 5)
            offset = (int(page) - 1) * int(items_per_page)

            paginator = Paginator(prod, items_per_page)
            try:
                products = paginator.page(page)
            except PageNotAnInteger:
                products = paginator.page(1)
            except EmptyPage:
                products = paginator.page(paginator.num_pages)

            serialized = ProductSerializer(products,  many=True).data
            
            response = {
                "status": 200,
                "success": True,
                "message": f"Products of {subcategory} returned",
                "page_number": int(page),
                "items_per_page": int(items_per_page),
                "total_products": paginator.count,
                "total_pages": paginator.num_pages,
                "data": serialized
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f'Server Malfunction {e}, we are fixing it'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
