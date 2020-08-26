from rest_framework import serializers

from apps.products.models import Unit, Product


class UnitSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Unit
        fields = '__all__'


class AmountSerializer(serializers.Serializer):
    unit = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Unit.objects.all()
    )

    quantity = serializers.DecimalField(max_digits=12, decimal_places=5)

    class Meta:
        fields = ['quantity', 'unit']
        abstract = True


class ProductSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class ProductMinimalSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Product
        fields = ['url', 'name']
