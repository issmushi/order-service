from rest_framework import serializers


class OrderItemInputSerializer(serializers.Serializer):
    good_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class CreateOrderSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    goods = OrderItemInputSerializer(many=True)
    promo_code = serializers.CharField(required=False, allow_null=True)