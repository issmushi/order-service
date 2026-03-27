from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema

from apps.orders.serializers import (
    CreateOrderSerializer,
    OrderOutputSerializer,
)
from apps.orders.services import create_order, GoodsInput


User = get_user_model()


class CreateOrderView(APIView):

    @extend_schema(
        request=CreateOrderSerializer,
        responses=OrderOutputSerializer,
    )
    def post(self, request):
        """
        API endpoint to create an order with optional promo code.
        """
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        try:
            user = User.objects.get(id=validated_data["user_id"])
        except User.DoesNotExist:
            raise ValidationError("User not found")

        goods_data = [
            GoodsInput(**item)
            for item in validated_data["goods"]
        ]

        result = create_order(
            user=user,
            goods_data=goods_data,
            promo_code_str=validated_data.get("promo_code"),
        )

        return Response(result, status=status.HTTP_201_CREATED)