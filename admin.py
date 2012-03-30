from django.contrib import admin
from django.db.models import get_models
from models import GeoMap, DataSources, Glossary, DescriptionOfMapUnits, MapUnitPolys, ContactsAndFaults, StandardLithology, RepresentativeValue, GeologicUnitView

class GeoMapAdmin(admin.ModelAdmin):
    search_fields = ['name', 'title']
admin.site.register(GeoMap, GeoMapAdmin)

class OwningMapFilterer(admin.ModelAdmin):
    list_filter = ('owningmap',)
    
for cls in [cls for cls in get_models() if cls._meta.app_label == "ncgmp" and cls._meta.object_name not in ["GeoMap"] ]:
    admin.site.register(cls, OwningMapFilterer)

