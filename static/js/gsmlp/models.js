var BaseRow = Backbone.Model.extend({
	toJSON: function() {
		var properties = _.clone(this.attributes);
		delete properties.id;
		return { 
			type: "Feature", 
			id: this.id, 
			properties: properties, 
			geometry: null
		}; 
	},
	
	parse: function(response) {
		var obj = { "id": response.id };
		return _.extend(obj, response.properties);
	}
});

var BaseCollection = Backbone.Collection.extend({
	urlRoot: "/ncgmp/gm/" + geomapId + "/",
	
	toJSON: function() { 
		var obj = {type: "FeatureCollection", features: []};
		this.models.forEach(function(model) {
			obj.features.push(model.toJSON());
		});
		return obj;
	},
	
	parse: function(response) { return response.features; }
});

var Lithology = BaseRow.extend({
	initialize: function(properties) {
		this.set("standardlithology_id", properties.standardlithology_id || guidGenerator());
		this.set("mapunit", properties.mapunit || null);
		this.set("parttype", properties.parttype || "http://resource.geosciml.org/classifier/cgi/geologicunitpartrole/0015");
		this.set("lithology", properties.lithology || "http://resource.geosciml.org/classifier/cgi/lithology/0225");
		this.set("proportionterm", properties.proportionterm || "http://resource.geosciml.org/classifier/cgi/proportionterm/0005");
		this.set("proportionvalue", properties.proportionvalue || null);
		this.set("scientificconfidence", properties.scientificconfidence || "std");
		this.set("datasourceid", properties.datasourceid || "Generic.Application.Generated");
	}
});

var RepValue = BaseRow.extend({
	initialize: function(properties) {
		this.set("mapunit", properties.mapunit || null);
		this.set("representativelithology_uri", properties.representativelithology_uri || null);
		this.set("representativeage_uri", properties.representativeage_uri || null);
		this.set("representativeolderage_uri", properties.representativeolderage_uri || null);
		this.set("representativeyoungerage_uri", properties.representativeyoungerage_uri || null);
	}
});

var GeologicEvent = BaseRow.extend({
	initialize: function(properties) {
		this.set("geologicevents_id", properties.geologicevents_id || guidGenerator());
		this.set("event", properties.event || "Missing");
		this.set("agedisplay", properties.agedisplay || "Missing");
		this.set("ageyoungerterm", properties.ageyoungerterm || "Missing");
		this.set("ageolderterm", properties.ageolderterm || "Missing");
		this.set("timescale", properties.timescale || "ICS 2009");
		this.set("ageyoungervalue", properties.ageyoungervalue || null);
		this.set("ageoldervalue", properties.ageoldervalue || null);
		this.set("notes", properties.notes || "");
		this.set("datasourceid", properties.datasourceid || "Generic.Application.Generated");
	}
});

var MapUnitDescription = BaseRow.extend({	
	initialize: function(properties) {
		this.set("descriptionofmapunits_id", properties.descriptionofmapunits_id || null);
		this.set("mapunit", properties.mapunit || null);
		this.set("label", properties.label || null);
		this.set("name", properties.name || null);
		this.set("fullname", properties.fullname || null);
		this.set("age", properties.age || null);
		this.set("description", properties.description || null);
		this.set("hierarchykey", properties.hierarchykey || null);
		this.set("paragraphstyle", properties.paragraphstyle || null);
		this.set("areafillrgb", properties.areafillrgb || null);
		this.set("areafillpatterndescription", properties.areafillpatterndescription || null);
		this.set("descriptionsourceid", properties.descriptionsourceid || null);
		this.set("generallithologyterm", properties.generallithologyterm || null);
		this.set("generallithologyconfidence", properties.generallithologyconfidence || null);
	},
	
	getLithologies: function(callbacks) {
		if (this.isNew()) { this.lithologies = null; }
		else {
			this.lithologies = new StandardLithology(null, {dmuId: this.id});
			this.lithologies.fetch(callbacks);
		}
	},
	
	getRepresentativeValues: function(callbacks) {
		if (this.isNew()) { this.representativeValues = null; }
		else {
			this.representativeValues = new RepresentativeValue(null, {dmuId: this.id});
			this.representativeValues.fetch(callbacks);
		}
	},
	
	getGeologicHistory: function(callbacks) {
		if (this.isNew()) { this.geologicHistory = null; }
		else {
			this.geologicHistory = new GeologicHistory(null, {dmuId: this.id});
			this.geologicHistory.fetch(callbacks);
		}
	},
	
	getPreferredAge: function(callbacks) {
		if (this.isNew()) { this.preferredAge = null; }
		else {
			this.preferredAge = new PreferredAge(null, {dmuId: this.id});
			this.preferredAge.fetch(callbacks);
		}
	}
});

var RepresentativeValue = BaseCollection.extend({
	model: RepValue,
	
	initialize: function(models, options) {
		BaseCollection.prototype.initialize.apply(this, arguments);
		this.url = this.urlRoot.concat("dmu/" + options.dmuId + "/rep/");
	}
});

var GeologicHistory = BaseCollection.extend({
	model: GeologicEvent,
	
	initialize: function(models, options) {
		this.url = this.urlRoot.concat("dmu/" + options.dmuId + "/age/");
	}
});

var PreferredAge = BaseCollection.extend({
	model: GeologicEvent,
	
	initialize: function(models, options) {
		this.url = this.urlRoot.concat("dmu/" + options.dmuId + "/preferredage/");
	}
});

var StandardLithology = BaseCollection.extend({
	model: Lithology,
	
	initialize: function(models, options) {
		this.url = this.urlRoot.concat("dmu/" + options.dmuId + "/lith/");
	}
});

var DescriptionOfMapUnits = BaseCollection.extend({
	model: MapUnitDescription,
	
	initialize: function(models, options) {
		this.url = this.urlRoot.concat("dmu/");
	}
});

var Vocabulary = Backbone.Model.extend({
	initialize: function(properties) {
		this.set("name", properties.name || null);
		this.set("url", properties.url || null);
	},
	
	getTerms: function(callbacks) {
		if (this.isNew()) { this.terms = null; }
		else {
			var termUrl = this.url() + "/term/";
			var collection;
			if (this.get("name") == "ICSTimeScale") {
				collection = Backbone.Collection.extend({
					model: AgeTerm,
					url: termUrl
				});
			} else {
				collection = Backbone.Collection.extend({
					model: VocabularyConcept,
					url: termUrl
				});
			}
			this.terms = new collection();
			this.terms.fetch(callbacks);
		}
	},
	
	resolveUri: function(uri) {
		for (t in this.terms.models) {
			var thisModel = this.terms.models[t];
			if (thisModel.get("uri") == uri) { return thisModel; } 
		}
		return null;
	}
});

var VocabularyConcept = Backbone.Model.extend({
	initialize: function(properties) {
		this.set("uri", properties.uri || null);
		this.set("label", properties.label || null);
		this.set("definition", properties.definition || null);
		this.set("vocabulary", properties.vocabulary || null);
	}
});

var AgeTerm = Backbone.Model.extend({
	initialize: function(properties) {
		this.set("uri", properties.uri || null);
		this.set("label", properties.label || null);
		this.set("olderage", properties.olderage || null);
		this.set("youngerage", properties.youngerage || null);
		this.set("vocabulary", properties.vocabulary || null);
	}
});

var Vocabularies = Backbone.Collection.extend({
	model: Vocabulary,
	
	url: "/ncgmp/vocab/",
	
	byName: function(name) {
		for (v in this.models) {
			var thisVocab = this.models[v];
			if (thisVocab.get("name") == name) { return thisVocab; }
		}
		return null;
	}
})
