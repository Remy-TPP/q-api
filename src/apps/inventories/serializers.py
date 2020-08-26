from rest_framework import serializers

from apps.products.models import Product, Amount
from apps.inventories.models import (Place,
                                     InventoryItem)
from apps.products.serializers import (AmountSerializer)


class PlaceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Place
        fields = '__all__'

    def create(self, validated_data):
        current_profile = self.context['request'].user.profile

        members = validated_data.pop('members') if 'members' in validated_data else []
        members.append(current_profile)

        place = Place.objects.create(**validated_data)
        place.members.set(members)

        return place


class InventoryItemSerializer(AmountSerializer):
    product = serializers.SlugRelatedField(slug_field='name', queryset=Product.objects.all())

    class Meta:
        model = InventoryItem
        fields = ['id', 'product']

    def create(self, validated_data):
        product = validated_data.get('product')
        place = validated_data.get('place')

        if place:
            existing_items = place.inventory.filter(product=product)
            if existing_items.exists():
                item = existing_items.first()
                item.add_amount(Amount(validated_data.get('quantity'), validated_data.get('unit').id))
            else:
                item = InventoryItem.objects.create(**validated_data)
        else:
            place = PlaceSerializer.create(self, {'name': 'Home'})
            item = InventoryItem.objects.create(**validated_data, place=place)

        return item
