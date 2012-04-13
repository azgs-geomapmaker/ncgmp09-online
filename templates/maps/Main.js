$(document).ready(function(){
	var map = new L.Map("leaflet-map");
	
	/* Tilestream Layer example: 
	var historicUrl = "http://opengis.azexperience.org/tiles/v2/azHistoric1880/{z}/{x}/{y}.png",
		historicLayer = new L.TileLayer(historicUrl, {maxZoom: 10}); */
	
	/* ESRI tiled service example: */
	var natGeoLayer = new L.TileLayer.ESRI("http://services.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer");
	
	/* Bing maps example: 
	var bingLayer = new L.TileLayer.Bing(<<Bing Maps API Key>>, "Road"); */
	
	/* WMS layer example: */
	var wmsUrl = "{{ gsconfig.BaseGeoserverUrl }}wms",
		wmsLayer = new L.TileLayer.WMS(wmsUrl, { 
			layers: "gsmlp:GeologicUnitView", 
			format: "image/png",
			styles: "{{ gm.name }}",
			transparent: true 
		}); 
	
	var ll = new L.LatLng({{ bottom }}, {{ left }}),
		ur = new L.LatLng({{ top }}, {{ right }}),
		bounds = new L.LatLngBounds(ll, ur);
	
	/* WFS GeoJSON layer example: 
	var wfsLayer = new L.GeoJSON.WFS("http://opengis.azexperience.org/geoserver/wfs", "vae:azhistoricmines", {
		pointToLayer: function(latlng) { return new L.CircleMarker(latlng); },
		popupObj: new JadeContent("templates/example.jade"),
		popupOptions: { maxWidth: 530, centered: false },
		hoverFld: "name"
	}); */
	
	map.fitBounds(bounds).addLayer(natGeoLayer);
	setTimeout(function() { map.addLayer(wmsLayer); }, 500);
});