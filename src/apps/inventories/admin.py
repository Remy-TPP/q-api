from django.contrib import admin

from apps.inventories.models import Place

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'all_members')
    ordering = ('pk',)

    def all_members(self, obj):
        return '\n'.join([str(member) for member in obj.members.all().distinct()])
