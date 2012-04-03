from django.core.exceptions import ValidationError
from django import forms
from ncgmp.models import GeoMap
from zipfile import ZipFile
import os, shutil

class UploadGeoMapForm(forms.Form):
    name = forms.CharField(max_length=50)
    title = forms.CharField(max_length=200)
    map_type = forms.ChoiceField(choices=(('Direct observation', 'New mapping'), ('Compilation', 'Compilation')))
    metadata_url = forms.URLField(required=False)
    db = forms.FileField()
    
    def clean_name(self):
        data = self.cleaned_data['name']
        data = data.replace(" ", "-").lower()
        usedNames = [gm.name for gm in GeoMap.objects.all() ]
        if data in usedNames:
            raise forms.ValidationError("A geologic map called \"" + data + "\" has already been uploaded.")
        return data
    
    def clean_db(self):
        data = self.cleaned_data['db']
        self.fgdbHandler = FgdbHandler(data, self) 
        
        if data.content_type != "application/zip":
            raise forms.ValidationError("Please upload a zipped File Geodatabase")
        else:            
            self.fgdbHandler.saveZipfile()
            self.fgdbHandler.unzipFile()
            self.fgdbHandler.validateFgdb()
        
        return data
    
class FgdbHandler():
    def __init__(self, data, uploadForm): 
        self.file = data
        self.name = uploadForm.cleaned_data['name']
        self.title = uploadForm.cleaned_data['title']
        self.map_type = uploadForm.cleaned_data['map_type']
        self.metadata_url = uploadForm.cleaned_data['metadata_url']
        self.errJson = None
        
    def saveZipfile(self):
        archiveFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads", "archives"))
        zipLocation = os.path.join(archiveFolder, self.name + ".zip")
        try:
            destination = open(zipLocation, "wb+")
            for chunk in self.file.chunks():
                destination.write(chunk)
            destination.close()
        except:
            raise forms.ValidationError("Failed to save the file that was uploaded. Please try again.")
        else:
            self.zipLocation = zipLocation
    
    def unzipFile(self):
        archive = ZipFile(self.zipLocation, "r")
        folders = set([ name.split("/")[0] for name in archive.namelist() ])
        
        if len(folders) != 1 or not list(folders)[0].endswith(".gdb"):
            raise forms.ValidationError("The file that was uploaded did not contain a File Geodatabase")                    
        else:
            fgdbName = list(folders)[0]                
            fgdbFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads", "fgdbs"))
            archive.extractall(fgdbFolder)
            self.fgdbLocation = os.path.join(fgdbFolder, fgdbName)
    
    def validateFgdb(self):
        self.newGeoMap = GeoMap(
            name=self.name, 
            title=self.title,
            map_type=self.map_type,
            metadata_url=self.metadata_url, 
            fgdb_path=self.fgdbLocation
        )
        try:
            self.newGeoMap.clean()
        except ValidationError as err:
            self.errJson = err.asJson
            os.remove(self.zipLocation)
            shutil.rmtree(self.fgdbLocation)
            raise forms.ValidationError("Your File Geodatabase failed NCGMP09 validation. Issues are listed below.")
        else:
            self.newGeoMap.save()