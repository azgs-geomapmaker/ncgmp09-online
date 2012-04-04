import rdflib

class VocabularyConcept:
    def __init__(self, uri, label, definition):
        self.uri = uri
        self.label = label
        self.definition = definition

class Vocabulary:
    vocabularyUrls = {
        "SimpleLithology": "http://resource.geosciml.org/201012RDF/SimpleLithology201012.rdf",
        "GeologicUnitPartRole": "http://resource.geosciml.org/201012RDF/GeologicUnitPartRole201012.rdf",
        "ProportionTerm": "http://resource.geosciml.org/201012RDF/ProportionTerm201012.rdf"               
    }
    
    definitionPredicate = rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#definition')
    classifierPrefix = "http://resource.geosciml.org/classifier/"
    
    def __init__(self, vocabulary):
        self.g = rdflib.Graph()
        self.g.parse(self.vocabularyUrls[vocabulary])
        
        subjects = set([subj for subj, pred, obj in self.g if str(subj).startswith(classifierPrefix)])
        
        self.concepts = []
        for s in subjects:
            newKwargs = { "uri": str(s), "label": "none", "definition": "none" }
            
            try:
                labels = self.g.preferredLabel(s) 
                if len(labels) > 0: newKwargs["label"] = str(labels[0][1])
            except UnicodeEncodeError:
                newKwargs["label"] = "Character encoding error"

            try:                
                definitions = [obj for obj in self.g.objects(subject=s, predicate=self.definitionPredicate)]
                if len(definitions) > 0: newKwargs["definition"] = str(definitions[0])
            except UnicodeEncodeError:
                newKwargs["definition"] = "Character encoding error"
                
            self.concepts.append(VocabularyConcept(**newKwargs))
            
        