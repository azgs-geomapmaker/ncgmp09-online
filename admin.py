from django.contrib import admin
from django.db.models import get_models

for cls in [ cls for cls in get_models() if cls._meta.app_label == "ncgmp" ]:
    admin.site.register(cls)
