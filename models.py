from django.contrib.gis.db import models
from django.core.exceptions import ValidationError

# Map is a class that represents the upload of a single NCGMP File Geodatabase
class GeoMap(models.Model):
    class Meta:
        db_table = 'geomaps'
        verbose_name = 'Geologic Maps'
        
    name = models.CharField(max_length=200)
    fgdb_path = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name
    
    def clean(self):
        # First, validate that the FGDB is valid
        from dataloader import validate_fgdb
        valid, message = validate_fgdb(self)
        if not valid:
            raise ValidationError(message)
    
    def load(self):
        class LoadError(Exception):
            "Loading data failed"
            pass
    
        from dataloader import load_data
        success, message = load_data(self)
        if not success:
            raise LoadError(message)

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
    mapunit = models.ForeignKey('DescriptionOfMapUnits', db_column='mapunit', to_field='mapunit')
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
    
    owningmap = models.ForeignKey('GeoMap')    
    contactsandfaults_id = models.CharField(max_length=200, unique=True)
    linetype = models.CharField(max_length=200)
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
        ordering = ['hierarchykey']
    
    owningmap = models.ForeignKey('GeoMap')    
    descriptionofmapunits_id = models.CharField(max_length=200, unique=True)
    mapunit = models.CharField(max_length=200, unique=True)
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
    
class DataSources(models.Model):
    class Meta:
        db_table = 'datasources'
        verbose_name = 'Data Source'
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
    