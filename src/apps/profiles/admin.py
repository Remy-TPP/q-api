from django.contrib import admin

from apps.profiles.models import Profile, FriendshipStatus


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # TODO: m2m fields such as profiletypes are required when they should be optional
    list_display = ('username', 'full_name', 'avatar')
    ordering = ('pk',)

    def full_name(self, obj):
        return ' '.join([n for n in [obj.user.first_name, obj.user.last_name] if n])

    def username(self, obj):
        return obj.user.username


admin.site.register(FriendshipStatus)
