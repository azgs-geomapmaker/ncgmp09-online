from django.db.models import get_model

class StandardLithologyProcessor:
    def __init__(self, descriptionofmapunits):
        self.dmu = descriptionofmapunits
        
    def guessRepresentativeLithology(self):
        repValue = self.dmu.representativeValue()
        
        stdLiths = self.dmu.standardlithology_set.all()
        dominantLiths = [ lith for lith in stdLiths if lith.proportionterm.upper() == "DOMINANT" ]
        
        if stdLiths.count() == 1: repValue.representativelithology_uri = stdLiths[0].lithology                        
        elif len(dominantLiths) > 0: repValue.representativelithology_uri = dominantLiths[0].lithology 
        
        repValue.save()
            
class GeologicEventProcessor:
    def __init__(self, descriptionofmapunits):
        self.dmu = descriptionofmapunits
        
    def guessRepresentativeAge(self):
        def getTheRightValue():
            pass
        
        repValue = self.dmu.representativeValue()
        
        ExtendedAttributes = get_model("ncgmp", "ExtendedAttributes")
        GeologicEvents = get_model("ncgmp", "GeologicEvents")
        
        extAttrs = ExtendedAttributes.objects.filter(ownerid=self.dmu.descriptionofmapunits_id)
        preferredAges = extAttrs.filter(property='preferredAge')
        
        
        if preferredAges.count() > 0: extAttr = preferredAges[0]
        elif extAttrs.count() > 0: extAttr = extAttrs[0]
        else: return
        
        # There's a lot of wacky logic here to deal with the wacky NCGMP encoding.
        # more later.
                            
        
class GlossaryProcessor:
    def __init__(self, geomap):
        self.gm = geomap