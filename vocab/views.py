from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from ncgmp.models import Vocabulary, VocabularyConcept, AgeTerm
from ncgmp.utils import SimpleJsonResponse

def updateVocabulary(req, vocabId):
    vocab = get_object_or_404(Vocabulary, pk=vocabId)
    vocab.update()
    return redirect("/admin/ncgmp/vocabulary/")

def vocabCollection(req):
    if req.method == "GET":
        return SimpleJsonResponse(Vocabulary.objects.all(), False)
    else:
        return HttpResponseNotAllowed(["GET"])

def vocabResource(req, vocabId):
    vocab = get_object_or_404(Vocabulary, pk=vocabId)
    if req.method == "GET":
        return SimpleJsonResponse([vocab])
    else:
        return HttpResponseNotAllowed(["GET"])
    
def termCollection(req, vocabId):
    vocab = get_object_or_404(Vocabulary, pk=vocabId)
    
    if req.method == "GET":
        uri = req.GET.get("uri", False)
        if uri:
            if vocab.name == "ICSTimeScale": term = get_object_or_404(vocab.ageterm_set.all(), uri=uri)
            else: term = get_object_or_404(vocab.vocabularyconcept_set.all(), uri=uri)
            return redirect("term/" + str(term.id) + "/")
        
        if vocab.name == "ICSTimeScale":
            terms = vocab.ageterm_set.all()
        else:
            terms = vocab.vocabularyconcept_set.all()
        
        return SimpleJsonResponse(terms, False)
    
    else:
        return HttpResponseNotAllowed(["GET"])
    
def termResource(req, vocabId, termId):
    vocab = get_object_or_404(Vocabulary, pk=vocabId)
    if vocab.name == "ICSTimeScale": term = get_object_or_404(vocab.ageterm_set.all(), pk=termId)
    else: term = get_object_or_404(vocab.vocabularyconcept_set.all(), pk=termId)
        
    if req.method == "GET": return SimpleJsonResponse([term])
    else: return HttpResponseNotAllowed(["GET"])