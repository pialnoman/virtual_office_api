from django.contrib import admin

# Register your models here.
from projects.forms import TDOForm
from projects.models import Tdo


class TDOAdmin(admin.ModelAdmin):
    # The forms to add and change user instances
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference the removed 'username' field
    form = TDOForm
    add_form = TDOForm


admin.site.register(Tdo, TDOAdmin)