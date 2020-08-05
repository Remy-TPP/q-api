from rest_framework import serializers

from apps.products.models import Unit, Amount, Product


class UnitSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Unit
        fields = '__all__'


class UnitMinimalSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Unit
        fields = ['url', 'short_name']


class AmountSerializer(serializers.ModelSerializer):
    unit = UnitMinimalSerializer()

    class Meta:
        model = Amount
        fields = ['quantity', 'unit']

    # TODO: create() that receives unit.[short_]name and stores corresponding pk


class ProductSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class ProductMinimalSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Product
        fields = ['url', 'name']
