from rest_framework import serializers


class OrderItemInputSerializer(serializers.Serializer):
    good_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class CreateOrderSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    goods = OrderItemInputSerializer(many=True)
    promo_code = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True
    )

    def validate_goods(self, value):
        if not value:
            raise serializers.ValidationError("Goods list cannot be empty")
        return value


class OrderItemOutputSerializer(serializers.Serializer):
    good_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    discount = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)


class OrderOutputSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    order_id = serializers.IntegerField()
    goods = OrderItemOutputSerializer(many=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    discount = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)