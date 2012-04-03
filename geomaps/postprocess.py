from django.db.models import get_model

class StandardLithologyProcessor:
    def __init__(self, descriptionofmapunits):
        self.dmu = descriptionofmapunits
        
    def guessRepresentativeLithology(self):                
        repValue = None
        repValues = self.dmu.representativevalue_set.all()
        if len(repValues) == 1: repValue = repValues[0]
        
        stdLiths = self.dmu.standardlithology_set.all()
        dominantLiths = [ lith for lith in stdLiths if lith.proportionterm.upper() == "DOMINANT" ]
        
        if repValue:
            if len(stdLiths) == 1: repValue.representativelithology_uri = stdLiths[0].lithology                
            elif len(dominantLiths) > 0: repValue.representativelithology_uri = dominantLiths[0].lithology            
            else: return repValue
        else:
            newKwargs = { "owningmap": self.dmu.owningmap, "mapunit": self.dmu }        
            if len(stdLiths) == 1: newKwargs['representativelithology_uri'] = stdLiths[0].lithology 
            elif len(dominantLiths) > 0: newKwargs['representativelithology_uri'] = dominantLiths[0].lithology
            
            RepresentativeValue = get_model("ncgmp", "RepresentativeValue")
            newRepValue = RepresentativeValue(**newKwargs)
            newRepValue.save()
            return newRepValue
            
class GeologicEventProcessor:
    def __init__(self, descriptionofmapunits):
        self.dmu = descriptionofmapunits
        
class GlossaryProcessor:
    def __init__(self, geomap):
        self.gm = geomap