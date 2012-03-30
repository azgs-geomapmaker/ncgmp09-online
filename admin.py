from django.contrib import admin
from models import GeoMap, DataSources, Glossary, DescriptionOfMapUnits, MapUnitPolys, ContactsAndFaults, StandardLithology, RepresentativeValue, GeologicUnitView

class GeoMapAdmin(admin.ModelAdmin):
    search_fields = ['name', 'title']
admin.site.register(GeoMap, GeoMapAdmin)

class DataSourcesAdmin(admin.ModelAdmin):
    list_filter = ('owningmap',)
admin.site.register(DataSources, DataSourcesAdmin)

class GlossaryAdmin(admin.ModelAdmin):
    list_filter = ('owningmap',)
admin.site.register(Glossary, GlossaryAdmin)

class DescriptionOfMapUnitsAdmin(admin.ModelAdmin):
    list_filter = ('owningmap',)
admin.site.register(DescriptionOfMapUnits, DescriptionOfMapUnitsAdmin)

class MapUnitPolysAdmin(admin.ModelAdmin):
    list_filter = ('owningmap',)
admin.site.register(MapUnitPolys, MapUnitPolysAdmin)

class ContactsAndFaultsAdmin(admin.ModelAdmin):
    list_filter = ('owningmap',)
admin.site.register(ContactsAndFaults, ContactsAndFaultsAdmin)

class StandardLithologyAdmin(admin.ModelAdmin):
    list_filter = ('owningmap',)
admin.site.register(StandardLithology, StandardLithologyAdmin)

class RepresentativeValueAdmin(admin.ModelAdmin):
    list_filter = ('owningmap',)
admin.site.register(RepresentativeValue, RepresentativeValueAdmin)

class GeologicUnitViewAdmin(admin.ModelAdmin):
    list_filter = ('owningmap',)
admin.site.register(GeologicUnitView, GeologicUnitViewAdmin)