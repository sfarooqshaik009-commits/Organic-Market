from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(
        source="products.count",
        read_only=True,
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "product_count",
        ]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True,
    )

    average_rating = serializers.FloatField(
        read_only=True,
    )

    total_reviews = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "farmer",
            "category",
            "category_name",
            "name",
            "description",
            "price",
            "stock_qty",
            "image",
            "is_available",
            "created_at",
            "average_rating",
            "total_reviews",
        ]
        read_only_fields = [
            "id",
            "farmer",
            "created_at",
            "average_rating",
            "total_reviews",
        ]