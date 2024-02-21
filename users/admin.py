from organizations.admin import SlcAdmin, SlcInlineAdmin
from users.forms import UserChangeForm, UserCreationForm
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from rangefilter.filter import DateRangeFilter
from django.utils.translation import ugettext_lazy as _
from users.models import CustomUser
from post_office.models import *

class UsersAdmin(UserAdmin):
    # The forms to add and change user instances
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference the removed 'username' field
    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Profile info'), {'fields': ('first_name', 'last_name', 'phone', 'id_card_mac', 'profile_pic')}),
        (_('Permissions'),
         {'fields': ('groups', 'is_active', 'is_staff', 'is_superuser',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2')}
         ),
    )
    inlines = [SlcInlineAdmin]

    def user_type(self, obj):
        """
        get group, separate by comma, and display empty string if user has no group
        """
        return ','.join([g.name for g in obj.groups.all()]) if obj.groups.count() else ''

    list_display = (
        'email', 'username', 'last_name', 'is_active'
    )
    list_display_links = ('username', 'email')
    list_filter = ['groups', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('date_joined',)
    readonly_fields = ('date_joined', 'last_login')


admin.site.register(CustomUser, UsersAdmin)


admin.site.unregister(Email)
admin.site.unregister(EmailTemplate)
admin.site.unregister(Attachment)
admin.site.unregister(Log)