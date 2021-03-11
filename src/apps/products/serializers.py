from rest_framework import serializers
from decimal import Decimal

from apps.products.models import Unit, Product


class UnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = Unit
        exclude = ['id', 'dimensionality']


class AmountSerializer(serializers.Serializer):
    unit = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Unit.objects.all(),
        allow_null=True
    )
    quantity = serializers.DecimalField(max_digits=12, decimal_places=3, allow_null=True)

    class Meta:
        fields = ['quantity', 'unit']
        abstract = True

    def to_representation(self, instance):
        """Convert `quantity` to rounded value."""
        ret = super().to_representation(instance)
        if (ret['quantity']):
            s = str(round(Decimal(ret['quantity']), 2))
            ret['quantity'] = s.rstrip('0').rstrip('.') if '.' in s else s
        return ret


class ProductSerializer(serializers.ModelSerializer):
    available_units = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'available_units']

    def get_available_units(self, obj):
        dimensionalities = obj.available_dimensionalities.split(',')
        units = UnitSerializer(Unit.objects.filter(dimensionality__in=dimensionalities), many=True)
        return units.data


class ProductMinimalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'name']
