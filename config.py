class GeoServerConfig:
    BaseGeoserverUrl = "http://localhost:8080/geoserver/"
    GeoserverAdminUser = "admin"
    GeoserverAdminSecret = "geoserver"
    
class DatabaseConfig:
    name = "django"
    user = "django"
    secret = "ncgmp"
    port = 5432
    host = "localhost"