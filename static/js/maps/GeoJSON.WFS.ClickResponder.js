var vocabs = new Vocabularies();
vocabs.fetch({ success: function(models, response) {
	models.each(function(model) {
		model.getTerms();
	});
}});

L.GeoJSON.WFS.ClickResponder = L.Class.extend({
	initialize: function(options) {
		L.Util.setOptions(this, options);
		this.getFeatureBaseUrl = this.options.url + "?request=GetFeature&outputformat=json&typename=" + this.options.featureType + "&version=" + this.options.version || "1.1.0";
		this.options.map.wfsClickResponse = this;
		this.options.map.on("click", this.getFeature);
	},

	getFeature: function(event) {
		var that = this.wfsClickResponse;
 		var cqlFilter = "&cql_filter=CONTAINS(" + that.options.geomFieldName + ", POINT (" + event.latlng.lng + " " + event.latlng.lat + "))";
		var getFeatureUrl = that.getFeatureBaseUrl + cqlFilter;	
		var url = that.options.proxyUrl ? that.options.proxyUrl + getFeatureUrl : getFeatureUrl
		
		$.ajax({
			url: url,
			type: "GET",
			success: function(response) {
				if (response.type && response.type == "FeatureCollection") {
					if (response.features.length > 0) {
						that.highlightFeature(response.features[0], event);
					}
				}
			},
			dataType: "json"
		});
	},
	
	highlightFeature: function(feature, clickEvent) {
		var options = this.options;
		var map = options.map; 
		if (map.highlightedFeature) { map.removeLayer(map.highlightedFeature); }
		map.highlightedFeature = featureLayer = new L.GeoJSON();
		featureLayer.on("featureparse", function(f) {
			f.layer.setStyle({ stroke: true, color: "#FFF000", weight: 3, opacity: 1.0, fill: false });
			
			if (options.popupObj && options.popupOptions) {
				var additionals = {};
				var lithVocab = vocabs.byName("SimpleLithology");
				var ageVocab = vocabs.byName("ICSTimeScale");

				additionals.representativeAge_label = lookupTerm(ageVocab, f.properties.representativeAge_uri);
				additionals.representativeLithology_label = lookupTerm(lithVocab, f.properties.representativeLithology_uri);
				additionals.representativeYoungerAge_label = lookupTerm(ageVocab, f.properties.representativeYoungerAge_uri);
				additionals.representativeOlderAge_label = lookupTerm(ageVocab, f.properties.representativeOlderAge_uri);
				_.extend(f.properties, additionals);
				
				opts = _.extend({ evt: clickEvent }, options.popupOptions);
				map.openPopup(options.popupObj.generatePopup(f, opts));
			}
		});		
		map.addLayer(featureLayer);
		featureLayer.addGeoJSON(feature);
	}
});

function lookupTerm(vocab, uri) {
	if (uri == "http://www.opengis.net/def/nil/OGC/0/missing") { return "Missing"; }
	else if (vocab.terms.where({uri: uri}).length == 0) { return uri; }
	else { return vocab.terms.where({uri: uri})[0].get("label"); }
}