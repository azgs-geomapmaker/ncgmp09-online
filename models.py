from django.contrib.gis.db import models
from django.contrib.gis.gdal import DataSource
from django.core.exceptions import ValidationError
from geomaps.validation import GdbValidator
from geomaps.dataloader import GdbLoader
from geomaps.postprocess import StandardLithologyProcessor
from gsconfig.layers import LayerGenerator
from gsmlp.generators import GeologicUnitViewGenerator

# Map is a class that represents the upload of a single NCGMP File Geodatabase
class GeoMap(models.Model):
    class Meta:
        db_table = 'geomaps'
        verbose_name = 'Geologic Map'
        
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    fgdb_path = models.CharField(max_length=200)
    map_type = models.CharField(max_length=200, choices=(('Direct observation', 'New mapping'), ('Compilation', 'Compilation')))
    metadata_url = models.URLField(blank=True)
    is_loaded = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name
    
    def clean(self):
        try: 
            self.dataSource = DataSource(self.fgdb_path)
        except:
            raise ValidationError(self.fgdb_path + " could not be opened by GDAL")
        else:
            validator = GdbValidator(self.dataSource)
            valid = validator.isValid()
            if not valid:
                err = ValidationError(validator.validationMessage())
                err.asJson = validator.logs.asJson()
                raise err
                
    def load(self):
        loader = GdbLoader(self)
        loader.load()
        self.is_loaded = True
        self.save()
        
    def createGsmlp(self):
        geologicUnitViewGen = GeologicUnitViewGenerator(self)
        geologicUnitViewGen.buildGeologicUnitViews()
        
    def createLayers(self):
        layerGen = LayerGenerator(self)
        return layerGen.createNewLayers()

# The following are classes from the GeoSciML Portrayal Schema

class GeologicUnitView(models.Model):
    class Meta:
        db_table = 'geologicunitview'
        verbose_name = "GeologicUnitView"
    
    owningmap = models.ForeignKey('GeoMap')
    identifier = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    geologicUnitType = models.CharField(max_length=200, blank=True)
    rank = models.CharField(max_length=200, blank=True)
    lithology = models.CharField(max_length=200, blank=True)
    geologicHistory = models.TextField()
    observationMethod = models.CharField(max_length=200, blank=True)
    positionalAccuracy = models.CharField(max_length=200, blank=True)
    source = models.CharField(max_length=200, blank=True)
    geologicUnitType_uri = models.CharField(max_length=200)
    representativeLithology_uri = models.CharField(max_length=200)
    representativeAge_uri = models.CharField(max_length=200)
    representativeLowerAge_uri = models.CharField(max_length=200)
    representativeUpperAge_uri = models.CharField(max_length=200)
    specification_uri = models.CharField(max_length=200)
    metadata_uri = models.CharField(max_length=200)
    genericSymbolizer = models.CharField(max_length=200, blank=True)
    shape = models.MultiPolygonField(srid=4326)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.identifier 

# The following are classes that represent tables from an NCGMP Database
#    Each class contains a ForeignKey to the GeoMap Class, which is the upload
#    that the feature came into the system with

class MapUnitPolys(models.Model):
    class Meta:
        db_table = 'mapunitpolys'
        verbose_name = 'Map Unit Polygon'
        verbose_name_plural = 'MapUnitPolys'
    
    owningmap = models.ForeignKey('GeoMap')    
    mapunitpolys_id = models.CharField(max_length=200, unique=True)
    mapunit = models.ForeignKey('DescriptionOfMapUnits', db_column='mapunit')
    identityconfidence = models.CharField(max_length=200)
    label = models.CharField(max_length=200, blank=True)
    symbol = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    datasourceid = models.ForeignKey('DataSources', db_column='datasourceid', to_field='datasources_id')
    shape = models.MultiPolygonField(srid=4326)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.mapunitpolys_id
    
class ContactsAndFaults(models.Model):
    class Meta:
        db_table = 'contactsandfaults'
        verbose_name = 'Contact or Fault'
        verbose_name_plural = 'ContactsAndFaults'
    
    owningmap = models.ForeignKey('GeoMap')    
    contactsandfaults_id = models.CharField(max_length=200, unique=True)
    type = models.CharField(max_length=200)
    isconcealed = models.IntegerField()
    existenceconfidence = models.CharField(max_length=200)
    identityconfidence = models.CharField(max_length=200)
    locationconfidencemeters = models.FloatField()
    label = models.CharField(max_length=200, blank=True)
    datasourceid = models.ForeignKey('DataSources', db_column='datasourceid', to_field='datasources_id')
    notes = models.TextField(blank=True)
    symbol = models.IntegerField()
    shape = models.MultiLineStringField(srid=4326)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.contactsandfaults_id
    
class DescriptionOfMapUnits(models.Model):
    class Meta:
        db_table = 'descriptionofmapunits'
        verbose_name = 'Description of a Map Unit'
        verbose_name_plural = 'DescriptionOfMapUnits'
        ordering = ['hierarchykey']
    
    owningmap = models.ForeignKey('GeoMap')    
    descriptionofmapunits_id = models.CharField(max_length=200, unique=True)
    mapunit = models.CharField(max_length=200)
    label = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    fullname = models.CharField(max_length=200)
    age = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    hierarchykey = models.CharField(max_length=200)
    paragraphstyle = models.CharField(max_length=200, blank=True)
    areafillrgb = models.CharField(max_length=200)
    areafillpatterndescription = models.CharField(max_length=200, blank=True)
    descriptionsourceid = models.ForeignKey('DataSources', db_column='descriptionsourceid', to_field='datasources_id')
    generallithologyterm = models.CharField(max_length=200, blank=True)
    generallithologyconfidence = models.CharField(max_length=200, blank=True)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.name
    
    def generateRepresentativeValues(self):
        StandardLithologyProcessor(self).guessRepresentativeLithology()
    
class DataSources(models.Model):
    class Meta:
        db_table = 'datasources'
        verbose_name = 'Data Source'
        verbose_name_plural = 'DataSources'
        ordering = ['source']
        
    owningmap = models.ForeignKey('GeoMap')
    datasources_id = models.CharField(max_length=200, unique=True)
    notes = models.TextField()
    source = models.CharField(max_length=200)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.source
    
class Glossary(models.Model):
    class Meta:
        db_table = 'glossary'
        verbose_name_plural = 'Glossary Entries'
        ordering = ['term']
    
    owningmap = models.ForeignKey('GeoMap')    
    glossary_id = models.CharField(max_length=200, unique=True)
    term = models.CharField(max_length=200)
    definition = models.CharField(max_length=200)
    definitionsourceid = models.ForeignKey('DataSources', db_column='descriptionsourceid', to_field='datasources_id')
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.term
    
class StandardLithology(models.Model):
    class Meta:
        db_table = 'standardlithology'
        verbose_name_plural = 'Standard Lithology'
    
    owningmap = models.ForeignKey('GeoMap')    
    standardlithology_id = models.CharField(max_length=200, unique=True)
    mapunit = models.ForeignKey('descriptionofmapunits', db_column='mapunit')
    parttype = models.CharField(max_length=200)
    lithology = models.CharField(max_length=200)
    proportionterm = models.CharField(max_length=200, blank=True)
    proportionvalue = models.FloatField(max_length=200, blank=True, null=True)
    scientificconfidence = models.CharField(max_length=200)
    datasourceid = models.ForeignKey('DataSources', db_column='datasourceid', to_field='datasources_id')
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.mapunit.mapunit + ': ' + self.lithology

class ExtendedAttributes(models.Model):
    class Meta:
        db_table = 'extendedattributes'
        verbose_name_plural = 'ExtendedAttributes'
        ordering = ['ownerid']
    
    owningmap = models.ForeignKey('GeoMap')    
    extendedattributes_id = models.CharField(max_length=200)
    ownertable = models.CharField(max_length=200)
    ownerid = models.CharField(max_length=200)
    property = models.CharField(max_length=200)
    propertyvalue = models.CharField(max_length=200, blank=True)
    valuelinkid = models.CharField(max_length=200, blank=True)
    qualifier = models.CharField(max_length=200, blank=True)
    notes = models.CharField(max_length=200, blank=True)
    datasourceid = models.ForeignKey('DataSources', db_column='datasourceid', to_field='datasources_id')
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.property + ' for ' + self.ownerid
    
class GeologicEvents(models.Model):
    class Meta:
        db_table = 'geologicevents'
        verbose_name_plural = 'GeologicEvents'
        ordering = ['event']
    
    owningmap = models.ForeignKey('GeoMap')    
    geologicevents_id = models.CharField(max_length=200)
    event = models.CharField(max_length=200)
    agedisplay = models.CharField(max_length=200)
    ageyoungerterm = models.CharField(max_length=200, blank=True)
    ageolderterm = models.CharField(max_length=200, blank=True)
    timescale = models.CharField(max_length=200, blank=True)
    ageyoungervalue = models.FloatField(blank=True, null=True)
    ageoldervalue = models.FloatField(blank=True, null=True)
    notes = models.CharField(max_length=200, blank=True)
    datasourceid = models.ForeignKey('DataSources', db_column='datasourceid', to_field='datasources_id')
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.event + ': ' + self.agedisplay
    
# The following are "helper" tables for generating GSMLP effectively

class RepresentativeValue(models.Model):
    class Meta:
        db_table = 'representativevalue'
        
    owningmap = models.ForeignKey('GeoMap') 
    mapunit = models.ForeignKey('descriptionofmapunits', db_column='mapunit')
    representativelithology_uri = models.CharField(max_length=200, blank=True)
    representativeage_uri = models.CharField(max_length=200, blank=True)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return "Representative values for " + self.mapunit.mapunit 