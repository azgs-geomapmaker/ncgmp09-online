from django.db.models import get_models

def test(request):
    a = get_models()
    print "Hello there"