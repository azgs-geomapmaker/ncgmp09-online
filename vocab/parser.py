from django.db.models import get_model
import rdflib

def updateVocabulary(vocab):
    def findAgeValue(graph, subj, boundaryPredicate):
        positionPred = rdflib.term.URIRef("http://resource.geosciml.org/schema/cgi/trs/3.0/position")
        valuePred = rdflib.term.URIRef("http://def.seegrid.csiro.au/isotc211/iso19108/2006/temporalobject/value")
        
        boundaries = [obj for obj in graph.objects(subj, boundaryPredicate)]
        if len(boundaries) > 0:
            boundary = boundaries[0]
            positions = [obj for obj in graph.objects(boundary, positionPred)]
            if len(positions) > 0:
                position = positions[0]
                values = [obj for obj in graph.objects(position, valuePred)]
                if len(values) > 0:
                    return str(values[0])
        return "None"
    
    vocab.vocabularyconcept_set.all().delete()
    vocab.ageterm_set.all().delete()
    
    definitionPredicate = rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#definition')
    typePredicate = rdflib.term.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")      
    eraObj = rdflib.term.URIRef("http://resource.geosciml.org/schema/cgi/gts/3.0/GeochronologicEra")
    classifierPrefix = "http://resource.geosciml.org/classifier/"
    
    g = rdflib.Graph()
    g.parse(vocab.url)
    
    if vocab.name == "ICSTimeScale":
        subjects = set([ subj for subj, pred, obj in g if pred == typePredicate and obj == eraObj ])
        newClass = get_model("ncgmp", "AgeTerm")
    else:
        subjects = set([subj for subj, pred, obj in g if str(subj).startswith(classifierPrefix)])
        newClass = get_model("ncgmp", "VocabularyConcept")
        
    concepts = []
    for s in subjects:
        newKwargs = { "uri": str(s), "label": "none", "vocabulary": vocab}
        
        try:
            labels = [l for p, l in g.preferredLabel(s) if l.language == 'en'] 
            if len(labels) > 0: newKwargs["label"] = str(labels[0])
        except UnicodeEncodeError:
            newKwargs["label"] = "Character encoding error"

        try:                
            definitions = [obj for obj in g.objects(subject=s, predicate=definitionPredicate)]
            if len(definitions) > 0: newKwargs["definition"] = str(definitions[0])
        except UnicodeEncodeError:
            newKwargs["definition"] = "Character encoding error"
        
        if vocab.name == "ICSTimeScale":
            startPred = rdflib.term.URIRef("http://resource.geosciml.org/schema/cgi/trs/3.0/start")
            endPred = rdflib.term.URIRef("http://resource.geosciml.org/schema/cgi/trs/3.0/end")
            newKwargs["olderage"] = findAgeValue(g, s, startPred)
            newKwargs["youngerage"] = findAgeValue(g, s, endPred)
        
        if newKwargs['label'] != 'none': 
            concepts.append(newClass(**newKwargs))
    newClass.objects.bulk_create(concepts)
    