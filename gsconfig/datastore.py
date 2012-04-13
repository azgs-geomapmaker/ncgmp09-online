from ncgmp.config import DatabaseConfig
import json

class PostGISDatastoreDef:
    def __init__(self, workspace):
        self.dbConfig = DatabaseConfig()
        
        self.workspace = {
            "name": workspace.name,
            "href": workspace.href
        }
        
        self.connectionParameters = [
            ("Connection timeout", "20"),
            ("port", self.dbConfig.port),
            ("passwd", self.dbConfig.secret),
            ("dbtype", "postgis"),
            ("host", self.dbConfig.host),
            ("validate connections", "false"),
            ("max connections", "10"),
            ("database", self.dbConfig.name),
            ("namespace", self.workspace["href"]),
            ("schema", "public"),
            ("Loose bbox", "true"),
            ("Expose primary keys", "false"),
            ("Max open prepared statements", "50"),
            ("preparedStatements", "false"),
            ("Estimated extends", "true"),
            ("user", self.dbConfig.user),
            ("min connections", "1"),
            ("fetch size", "1000"),                                         
        ]
        
    def serialize(self):
        return json.dumps({
            "dataStore": {
                "name": "django",
                "type": "PostGIS",
                "enabled": True,
                "workspace": self.workspace,
                "connectionParameters": {
                    "entry": [{"@key": key[0], "$": key[1]} for key in self.connectionParameters]                        
                },
                "__default": False
            }           
        })