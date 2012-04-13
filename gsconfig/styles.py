from ncgmp.config import GeoServerConfig
from ncgmp.dmu.dmu import dmuContentNegotiation
from catalog import Catalog

class StyleGenerator:
    def __init__(self, geomap):
        self.gm = geomap
        self.cat = Catalog(GeoServerConfig.BaseGeoserverUrl + "rest", GeoServerConfig.GeoserverAdminUser, GeoServerConfig.GeoserverAdminSecret)
        
    def createStyle(self):
        dmus = self.gm.descriptionofmapunits_set.all()
        sldResponse = dmuContentNegotiation("application/sld", dmus)
        if sldResponse.status_code == 200:
            sld = sldResponse.content
            if self.cat.get_style(self.gm.name) is not None: overwrite = True
            else: overwrite = False
            try:
                self.cat.create_style(self.gm.name, sld, overwrite)
            except Exception as ex:
                raise ex