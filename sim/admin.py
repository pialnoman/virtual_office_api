# from admin_totals.admin import ModelAdminTotals
from django.contrib import admin
# from import_export.admin import ExportMixin
from sim.models import SIMCard
from .resources import SIMCardResource
from django.db.models import Sum
# Register your models here.

class SIMCardAdmin(admin.ModelAdmin):
    resource_class = SIMCardResource
    list_display = ('sim_number', 'phone_number','amount','activation_status', 'project', 'assignee')
    list_filter = ( 'activation_status', 'project', 'assignee', 'sim_operator')
    search_fields = ('sim_number', 'phone_number', 'imei_number', 'project', 'deployment_location', "assignee", 'sim_operator')
    list_totals = [('amount', Sum)]    
admin.site.register(SIMCard, SIMCardAdmin)
