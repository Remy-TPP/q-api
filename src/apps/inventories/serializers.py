from rest_framework import serializers

from apps.inventories.models import (Place,
                                     Inventory,
                                     InventoryItem)

class PlaceSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = InventoryItem
        fields = '__all__'
