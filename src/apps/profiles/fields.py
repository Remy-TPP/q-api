from rest_framework import serializers


class EventField(serializers.HyperlinkedRelatedField):
    def to_representation(self, value):
        url = super(EventField, self).to_representation(value)
        return {
            'url': url,
            'name': str(value)
        }


class AttendeeField(serializers.RelatedField):
    def to_representation(self, value):
        return {
            'id': value.id,
            'name': str(value)
        }
