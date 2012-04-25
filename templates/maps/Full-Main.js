$(document).ready(function(){
	var map = new L.Map("leaflet-map");
	
	/* ESRI tiled service example: */
	var natGeoLayer = new L.TileLayer.ESRI("http://services.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer");
	
	/* WMS layer example: */
	var wmsUrl = "{{ gsconfig.BaseGeoserverUrl }}wms",
		wmsLayer = new L.TileLayer.WMS(wmsUrl, { 
			layers: "gsmlp:GeologicUnitView", 
			format: "image/png",
			styles: "{{ gm.name }}",
			transparent: true,
			opacity: 0.7
		}); 
	
	/* Build a legendPanel */
	var sidePanel = new L.Control.Panel({
		id: "side-panel",
		width: 450,
		url: "/ncgmp/gm/{{ gm.id }}/dmu/",
		title: "{{ gm.title }}"
	});
	
	/* Add a WFS Click Response */
	map.clickResponse = new L.GeoJSON.WFS.ClickResponder({
		map: map,
		url: "{{ gsconfig.BaseGeoserverUrl }}wfs",
		featureType: "gsmlp:GeologicUnitView",
		version: "1.0.0",
		geomFieldName: "shape",
		popupObj: new JadeContent("/static/templates/geounit-popup.jade"),
		popupOptions: { maxWidth: 530, centered: false },
		proxyUrl: "/ncgmp/proxy?url="
	});
	
	var ll = new L.LatLng({{ bottom }}, {{ left }}),
		ur = new L.LatLng({{ top }}, {{ right }}),
		bounds = new L.LatLngBounds(ll, ur);
	
	map.fitBounds(bounds).addLayer(natGeoLayer).addControl(sidePanel);
	setTimeout(function() { map.addLayer(wmsLayer); }, 500);
});