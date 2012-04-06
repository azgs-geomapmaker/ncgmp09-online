from django.db.models import get_model
from ncgmp.vocab.parser import Vocabulary

timescale = Vocabulary("ICSTimeScale")
lithology = Vocabulary("SimpleLithology")

timescaleUris = [c.uri for c in timescale.concepts]
lithologyUris = [c.uri for c in lithology.concepts]

class StandardLithologyProcessor:
    def __init__(self, descriptionofmapunits):
        self.dmu = descriptionofmapunits
        
    def guessRepresentativeLithology(self):
        repValue = self.dmu.representativeValue()
        
        stdLiths = self.dmu.standardlithology_set.all()
        dominantLiths = [ lith for lith in stdLiths if lith.proportionterm.upper() == "DOMINANT" ]
        
        if stdLiths.count() == 1 and stdLiths[0].lithology in lithologyUris: repValue.representativelithology_uri = stdLiths[0].lithology                        
        elif len(dominantLiths) > 0 and dominantLiths[0].lithology in lithologyUris: repValue.representativelithology_uri = dominantLiths[0].lithology 
        
        repValue.save()
            
class GeologicEventProcessor:
    def __init__(self, descriptionofmapunits):
        self.dmu = descriptionofmapunits
    
    def _getOne(self, theModel, kwargs):
        try:
            theModel.objects.get(**kwargs)
        except theModel.MultipleObjectsReturned:
            return theModel.objects.filter(**kwargs)[0]
        except theModel.DoesNotExist:
            return None
            
    def guessRepresentativeAge(self):
        repValue = self.dmu.representativeValue()        
        
        ExtendedAttributes = get_model("ncgmp", "ExtendedAttributes")
        GeologicEvents = get_model("ncgmp", "GeologicEvents")
        
        extAttrs = ExtendedAttributes.objects.filter(ownerid=self.dmu.descriptionofmapunits_id)
        geologicEvents = GeologicEvents.objects.filter(geologicevents_id__in=extAttrs.values_list("valuelinkid", flat=True))
        
        # There are no ExtendedAttributes and the dmu.Age field contains a timescale URI
        if extAttrs.count() == 0 and self.dmu.age in timescaleUris:
            repValue.representativeage_uri = self.dmu.age
        
        geologicEvent = None
        preferredAge = self._getOne(ExtendedAttributes, { "property__iexact": "preferredAge" })
        
        # There is a preferredAge related to a GeologicEvent
        if preferredAge != None and preferredAge.valuelinkid != '':
            geologicEvent = self._getOne(GeologicEvents, { "geologicevents_id": preferredAge.valuelinkid })
        # There is a preferredAge and it has a propertyValue that is a timescale URI
        elif preferredAge != None and preferredAge.propertyvalue in timescaleUris:
            repValue.representativeage_uri = preferredAge.propertyvalue
        # There is exactly one linked GeologicEvent
        elif geologicEvents.count() == 1:
            geologicEvent = geologicEvents[0]
        
        # A GeologicEvent was selected to contain representative values
        if geologicEvent != None:
            if geologicEvent.agedisplay in timescaleUris:
                repValue.representativeage_uri = geologicEvent.agedisplay
            if geologicEvent.ageyoungerterm in timescaleUris:
                repValue.representativeyoungerage_uri = geologicEvent.ageyoungerterm
            if geologicEvent.ageolderterm in timescaleUris:
                repValue.representativeolderage_uri = geologicEvent.ageolderterm
                
        repValue.save()                        
        
class GlossaryProcessor:
    def __init__(self, geomap):
        self.gm = geomap