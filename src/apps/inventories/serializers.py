from rest_framework import serializers

from apps.products.models import Amount, Product
from apps.inventories.models import (Place,
                                     InventoryItem,
                                     Purchase,
                                     PurchaseItem,
                                     )
from apps.products.serializers import AmountSerializer


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


class InventoryItemSerializer(serializers.ModelSerializer):
    amount = AmountSerializer()
    product = serializers.SlugRelatedField(slug_field='name', queryset=Product.objects.all())

    class Meta:
        model = InventoryItem
        fields = ['id', 'product', 'amount']

    def create(self, validated_data):
        amount_serializer = AmountSerializer(data=validated_data.pop('amount'))
        if not amount_serializer.is_valid():
            raise serializers.ValidationError(amount_serializer.errors)

        product = validated_data.get('product')
        place = validated_data.get('place')

        if place:
            existing_items = place.inventory.filter(product=product)
            if existing_items.exists():
                item = existing_items.first()
                item.add_amount(Amount(**amount_serializer.validated_data))
            else:
                validated_data['amount'] = amount_serializer.save()
                item = InventoryItem.objects.create(**validated_data)
        else:
            validated_data['amount'] = amount_serializer.save()
            place = PlaceSerializer.create(self, {'name': 'Home'})
            item = InventoryItem.objects.create(**validated_data, place=place)

        return item


class PurchaseItemSerializer(serializers.ModelSerializer):
    amount = AmountSerializer()
    product = serializers.SlugRelatedField(slug_field='name', queryset=Product.objects.all())

    class Meta:
        model = PurchaseItem
        fields = ['id', 'product', 'amount']

    def create(self, validated_data):
        assert 'purchase' in validated_data.keys()

        amount_serializer = AmountSerializer(data=validated_data.pop('amount'))
        if not amount_serializer.is_valid():
            raise serializers.ValidationError(amount_serializer.errors)
        validated_data['amount'] = amount_serializer.save()

        return PurchaseItem(**validated_data)
        # TODO: (discuss) is it okay for a Serializer.create() to not actually save to db?


class PurchaseSerializer(serializers.HyperlinkedModelSerializer):
    items = PurchaseItemSerializer(many=True)

    class Meta:
        model = Purchase
        fields = '__all__'

    def create(self, validated_data):
        purchase_items_serializer = PurchaseItemSerializer(data=validated_data.pop('items'), many=True)
        if not purchase_items_serializer.is_valid():
            raise TypeError(purchase_items_serializer.errors)

        purchase = Purchase.objects.create()

        items_no_dupes = {}
        for purchase_item in purchase_items_serializer.save(purchase=purchase):
            if (existing_pi := items_no_dupes.get(purchase_item.product.name, None)):
                existing_pi.add_amount(purchase_item.amount)
            else:
                items_no_dupes[purchase_item.product.name] = purchase_item

        PurchaseItem.objects.bulk_create(items_no_dupes.values())

        return purchase

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError({'items': "Can't be empty"})
        return items
