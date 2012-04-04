import rdflib

class VocabularyConcept:
    def __init__(self, uri, label, definition, attributes):
        self.uri = uri
        self.label = label
        self.definition = definition
        self.attributes = attributes

class TimescaleEra(VocabularyConcept):
    def __init__(self, uri, label, older, younger, attributes):
        VocabularyConcept.__init__(self, uri, label, "None", attributes)
        self.olderAge = older
        self.youngerAge = younger
        
class Vocabulary:
    vocabularyUrls = {
        "SimpleLithology": "http://resource.geosciml.org/201012RDF/SimpleLithology201012.rdf",
        "GeologicUnitPartRole": "http://resource.geosciml.org/201012RDF/GeologicUnitPartRole201012.rdf",
        "ProportionTerm": "http://resource.geosciml.org/201012RDF/ProportionTerm201012.rdf",
        "ICSTimeScale": "http://services.azgs.az.gov/temp/isc-2009.rdf"             
    }
    
    definitionPredicate = rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#definition')
    typePredicate = rdflib.term.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")      
    eraObj = rdflib.term.URIRef("http://resource.geosciml.org/schema/cgi/gts/3.0/GeochronologicEra")
    
    classifierPrefix = "http://resource.geosciml.org/classifier/"
    
    def __init__(self, vocabulary):
        self.g = rdflib.Graph()
        self.g.parse(self.vocabularyUrls[vocabulary])
        
        if vocabulary == "ICSTimeScale":
            self.subjects = set([ subj for subj, pred, obj in self.g if pred == self.typePredicate and obj == self.eraObj ])
            newClass = TimescaleEra
        else:
            self.subjects = set([subj for subj, pred, obj in self.g if str(subj).startswith(self.classifierPrefix)])
            newClass = VocabularyConcept
        
        self.concepts = []
        for s in self.subjects:
            newKwargs = { "uri": str(s), "label": "none", "attributes": [(pred, obj) for pred, obj in self.g.predicate_objects(s)] }
            
            try:
                labels = [l for p, l in self.g.preferredLabel(s) if l.language == 'en'] 
                if len(labels) > 0: newKwargs["label"] = str(labels[0])
            except UnicodeEncodeError:
                newKwargs["label"] = "Character encoding error"

            try:                
                definitions = [obj for obj in self.g.objects(subject=s, predicate=self.definitionPredicate)]
                if len(definitions) > 0: newKwargs["definition"] = str(definitions[0])
            except UnicodeEncodeError:
                newKwargs["definition"] = "Character encoding error"
            
            if vocabulary == "ICSTimeScale":
                startPred = rdflib.term.URIRef("http://resource.geosciml.org/schema/cgi/trs/3.0/start")
                endPred = rdflib.term.URIRef("http://resource.geosciml.org/schema/cgi/trs/3.0/end")
                newKwargs["older"] = self._findAgeValue(s, startPred)
                newKwargs["younger"] = self._findAgeValue(s, endPred)
             
            self.concepts.append(newClass(**newKwargs))
            
    def _findAgeValue(self, subj, boundaryPredicate):
        positionPred = rdflib.term.URIRef("http://resource.geosciml.org/schema/cgi/trs/3.0/position")
        valuePred = rdflib.term.URIRef("http://def.seegrid.csiro.au/isotc211/iso19108/2006/temporalobject/value")
        
        boundaries = [obj for obj in self.g.objects(subj, boundaryPredicate)]
        if len(boundaries) > 0:
            boundary = boundaries[0]
            positions = [obj for obj in self.g.objects(boundary, positionPred)]
            if len(positions) > 0:
                position = positions[0]
                values = [obj for obj in self.g.objects(position, valuePred)]
                if len(values) > 0:
                    return str(values[0])
        return "None"
            
        