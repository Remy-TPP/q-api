from rest_framework import serializers

from apps.products.models import Unit, Amount, Product


class UnitSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Unit
        fields = '__all__'


class AmountSerializer(serializers.ModelSerializer):
    unit = serializers.SlugRelatedField(
        slug_field='short_name',
        queryset=Unit.objects.all()
    )

    class Meta:
        model = Amount
        fields = ['quantity', 'unit']


class ProductSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class ProductMinimalSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Product
        fields = ['url', 'name']
