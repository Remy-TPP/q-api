from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from django_better_admin_arrayfield.models.fields import ArrayField as DynamicArrayField

from apps.recipes.models import DishCategory, DishLabel, Dish, Recipe, RecipeInstructions, Ingredient
from common.widgets import DynamicArrayTextareaWidget


@admin.register(DishCategory)
class DishCategoryAdmin(admin.ModelAdmin):
    ordering = ('name',)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super(DishCategoryAdmin, self).get_form(request, obj, change, **kwargs)
        form.base_fields['description'].widget = admin.widgets.AdminTextareaWidget()
        return form


@admin.register(DishLabel)
class DishLabelAdmin(admin.ModelAdmin):
    ordering = ('name',)


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'labels_str')
    ordering = ('name',)

    def labels_str(self, obj):
        return ', '.join([label.name for label in obj.labels.all()])
    labels_str.short_description = "Labels"


# TODO: would be cleaner to embed these inline on their respective recipes instead of registering
@admin.register(RecipeInstructions)
class RecipeInstructionsAdmin(admin.ModelAdmin, DynamicArrayMixin):
    list_display = ('recipe',)
    ordering = ('recipe__title',)
    save_on_top = True
    readonly_fields = ('recipe',)
    fields = ('recipe', 'steps',)
    formfield_overrides = {
        DynamicArrayField: {'widget': DynamicArrayTextareaWidget},
    }

    def get_queryset(self, request):
        qs = super(RecipeInstructionsAdmin, self).get_queryset(request)
        return qs.filter(recipe__isnull=False)


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'dish')
    ordering = ('title',)
    save_on_top = True
    inlines = [IngredientInline]
    exclude = ('instructions',)
    readonly_fields = ('show_instructions', 'show_ingredients')

    fieldsets = (
        (None, {
            'fields': ('dish', 'title', 'description', 'image'),
        }),
        ('Instructions', {
            'fields': ('show_instructions', 'show_ingredients'),
        }),
    )

    def show_instructions(self, obj):
        return obj.instructions.displayable_steps
    show_instructions.short_description = 'Steps'

    def show_ingredients(self, obj):
        return obj.displayable_ingredients
    show_ingredients.short_description = 'Ingredients'

    def response_change(self, request, obj):
        """If pressing SAVE, redirect to next Recipe by title, if there is one; else use default behaviour."""
        if ('_continue' not in request.POST) \
                and (next_recipe := Recipe.objects.filter(title__gt=obj.title).order_by('title').first()):
            msg = format_html(_('Changed successfully. Redirected to next recipe by name.'))
            self.message_user(request, msg, messages.SUCCESS)
            return HttpResponseRedirect(f'../../{next_recipe.pk}/change')
        return super(RecipeAdmin, self).response_change(request, obj)
