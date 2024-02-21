from import_export import resources
from .models import SIMCard

class SIMCardResource(resources.ModelResource):
    class Meta:
        model = SIMCard

