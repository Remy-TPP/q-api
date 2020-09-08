from django.contrib import admin

from apps.products.models import Unit, Product


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name')
    ordering = ('pk',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    ordering = ('name',)
