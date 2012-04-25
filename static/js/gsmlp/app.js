var TermMappingApp = Backbone.View.extend({
	el: $("#term-mapping-app"),
	
	dmus: new DescriptionOfMapUnits(),
	
	vocabs: new Vocabularies(),
	
	initialize: function() {
		this.dmus.fetch({ success: this.addDmus });
		this.vocabs.fetch({ success: function(models, response) {
			models.each(function(model) {
				model.getTerms();
			});
		}});
	},
	
	addDmus: function(dmus, response) {
		dmus.each(function(dmu) {
			var dmuView = new DmuListItem({ model: dmu, id: "dmu-item-" + dmu.id });
			$("#mapunit-list").append(dmuView.render().el);
		});
	},
	
	vocabularyLookup: function(vocabName, uri) {
		var vocab = this.vocabs.byName(vocabName);
		term = vocab.resolveUri(uri);
		return term ? term.get("label") : uri;
	}
});

var application = new TermMappingApp();

