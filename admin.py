from django.contrib import admin
from django.db.models import get_models
from models import GeoMap, Vocabulary, VocabularyConcept, AgeTerm

class GeoMapAdmin(admin.ModelAdmin):
    search_fields = ['name', 'title']
admin.site.register(GeoMap, GeoMapAdmin)

class OwningMapFilterer(admin.ModelAdmin):
    list_filter = ('owningmap',)
    
for cls in [cls for cls in get_models() if cls._meta.app_label == "ncgmp" and cls._meta.object_name not in ["GeoMap", "Vocabulary", "VocabularyConcept", "AgeTerm"] ]:
    admin.site.register(cls, OwningMapFilterer)

class ConceptAdmin(admin.ModelAdmin):
    list_filter = ('vocabulary',)
    search_fields = ['label', 'definition']
    list_display = ('label', 'definition', 'uri')
    readonly_fields = ['label', 'definition', 'uri', 'vocabulary']
    actions = None
    
    def __init__(self, *args, **kwargs):
        super(ConceptAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None,)
        
class AgeTermAdmin(admin.ModelAdmin):
    list_filter = ('vocabulary',)
    search_fields = ['label']
    list_display = ('label', 'olderage', 'youngerage', 'uri')
    readonly_fields = ['label', 'olderage', 'youngerage', 'uri', 'vocabulary']
    actions = None
    
    def __init__(self, *args, **kwargs):
        super(AgeTermAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None,)
        
class VocabAdmin(admin.ModelAdmin):
    def update_vocabulary(self, obj):
        return "<a href='/ncgmp/vocab/%s/update/'>Update</a>" % obj.id
    update_vocabulary.allow_tags = True
    
    def number_of_terms(self, obj):
        return obj.vocabularyconcept_set.all().count() + obj.ageterm_set.all().count()
    
    def view_terms(self, obj):
        if obj.name == "ICSTimeScale":
            return "<a href='/admin/ncgmp/ageterm/?vocabulary__id__exact=%s'>%s Terms</a>" % (obj.id, obj.name)
        else:
            return "<a href='/admin/ncgmp/vocabularyconcept/?vocabulary__id__exact=%s'>%s Terms</a>" % (obj.id, obj.name)
    view_terms.allow_tags = True
    
    list_display = ('__unicode__', 'number_of_terms', 'view_terms', 'update_vocabulary')
    actions = None
    
    def __init__(self, *args, **kwargs):
        super(VocabAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None,)
        
admin.site.register(Vocabulary, VocabAdmin)
admin.site.register(VocabularyConcept, ConceptAdmin)
admin.site.register(AgeTerm, AgeTermAdmin)
