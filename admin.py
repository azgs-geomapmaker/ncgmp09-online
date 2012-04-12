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

class TermAdmin(admin.ModelAdmin):
    list_filter = ('vocabulary',)
    
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
    
admin.site.register(Vocabulary, VocabAdmin)
admin.site.register(VocabularyConcept, TermAdmin)
admin.site.register(AgeTerm, TermAdmin)
