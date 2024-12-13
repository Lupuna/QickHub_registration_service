from django.contrib import admin
from user_profile.models import User, Link, Customization,Notifications,Reminders


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email')
    list_display_links = ('id', 'email')


admin.site.register(Link)
admin.site.register(Customization)
admin.site.register(Notifications)
admin.site.register(Reminders)