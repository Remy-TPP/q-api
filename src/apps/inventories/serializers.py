from rest_framework import serializers

from apps.inventories.models import (Place,
                                     Inventory,
                                     InventoryItem)
from apps.products.serializers import (AmountSerializer)


class PlaceSerializer(serializers.HyperlinkedModelSerializer):
    inventory = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Place
        fields = '__all__'

    def create(self, validated_data):
        current_profile = self.context['request'].user.profile

        members = validated_data.pop('members') if 'members' in validated_data else []
        members.append(current_profile)

        new_inventory = Inventory.objects.create()

        place = Place.objects.create(**validated_data, inventory=new_inventory)
        place.members.set(members)
        return place


class InventorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Inventory
        fields = ['id', 'name', 'items', 'products']


class InventoryItemSerializer(serializers.ModelSerializer):
    amount = AmountSerializer()

    class Meta:
        model = InventoryItem
        fields = ['id', 'product', 'amount']

    def create(self, validated_data):
        amount_serializer = AmountSerializer(data=validated_data.pop('amount'))
        if not amount_serializer.is_valid():
            raise TypeError(amount_serializer.errors)

        product = validated_data['product']
        existing_items = validated_data['inventory'].items.filter(product=product)
        if existing_items.exists():
            item = existing_items.first()
            item.add_amount(amount_serializer.data)
        else:
            validated_data['amount'] = amount_serializer.save()
            item = InventoryItem.objects.create(**validated_data)

        return item
