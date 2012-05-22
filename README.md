## Introduction
Well, you're a geologist. You make geologic maps. Maybe your mapping is funded by the STATEMAP program. Maybe it isn't. You just spent half a year working on a handful of maps. You like them. You did a good job. They're pretty.
After you're done, you print them off on pieces of paper. You put one copy in a big drawer somewhere. You send another to the USGS and they put it is another big drawer somewhere else.
Once in a while (or maybe just once), someone takes your map out of the drawer and looks at it.
You're tired of paper. You've realized that people (yourself included) these days do almost all their learning on the internet. You want people to learn about all the cool information that you've put on your geologic map. You want people to be able to see it. You want people to be able to grab your data and compare it to their own. You want to grab other people's data and compare it to yours.
You need a way to publish your geologic map data online. So, I made this thing.

###What does it do?
What it allows you to do is upload your data in a format that geologists commonly use to produce their geologic maps: ESRI File Geodatabases.
Once you've uploaded your data, this program provides you an opportunity to describe your map units using standard vocabulary terminology. This makes your data more useful to other people by harmonizing the ways that we all talk about geologic things.
It creates a standards-based OGC Web Mapping Service that portrays your geologic map. Colored and everything. A huge number of client applications (including ArcMap) can connect to this service and allow people to see your map on their desktop.
It creates another service, this time an OGC Web Feature Service. This service conveys your data to the world, feature by feature, attribute by attribute. It maps your original data into GeoSciML-Portrayal features, a rapidly-developing and interoperable way to share geologic map data.
It makes a big, pretty web-page you can send your friends to so they can look at your map. The map shows off all your map unit descriptions in a nice legend panel. Your friends can click on any of the features (faults, structure measurements, whatever) on your map and get some more information about those features.

###What's the catch?
You have to upload the data as an ESRI File Geodatabase, and the structure of that File Geodatabase has to conform to the NCGMP09 database design standard. If that's hard to do, let's talk about how to make it easier.
You also have to run the application on a web server somewhere. This requires one or two little server-side backflips, but I'm happy to help you work through them.

## Installation
You'll need a web server with these things installed:
- GDAL version 1.9.0
- Django version > 1.3.1
- PostgreSQL 9.1
- pyjade 1.0.0
- Tomcat6
- Geoserver 2.1.3
- [gsconfig.py](https://github.com/dwins/gsconfig.py)
- [rdflib](https://github.com/RDFLib/rdflib)
- [mimeparse](http://code.google.com/p/mimeparse/)

Here is an [Installation Guide](https://github.com/usgin/ncgmp/wiki/Installation-Example) for running on a new Ubuntu Server.

## Ryan's Reminders...
- "Generic.Application.Generated" Datasource
