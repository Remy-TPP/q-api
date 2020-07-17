from django.contrib import admin

from apps.products.models import Unit, Product


# admin.site.register(Unit)
@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name')
    ordering = ('pk',)


admin.site.register(Product)
