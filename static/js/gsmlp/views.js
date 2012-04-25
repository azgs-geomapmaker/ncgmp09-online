var currentDmuInfo;

var DmuInfo = Backbone.View.extend({
	
	initialize: function(options) {
		this.listItem = options.listItem;
		this.$el = $("#mapunit-info");
	},
	
	template: _.template($("#dmu-info-tmpl").html()),
	
	render: function() {
		context = _.extend({}, this.model.toJSON().properties, { "height": $("#mapunit-list").height() + 15 });
		this.$el.html(this.template(context));
		return this;
	},
	
	events: {
		"click .controls li": "controlsClick"
	},
	
	controlsClick: function(event) {
		var target = $(event.target);
		var action = target.hasClass("add") ? "add" : target.hasClass("remove") ? "remove" : "none";
		var collection = this.model[target.parent("ul").attr("for")];
		var refreshList = ({
			"lithologies": this.listItem.addLithologies,
			"preferredAge": this.listItem.addPreferredAge,
			"geologicHistory": this.listItem.addEvents,
		})[target.parent("ul").attr("for")];
		
		if (action == "add") {
			collection.create(new collection.model({ "mapunit": this.model.id }), { success: function() { refreshList(collection); } });
		} else {
			target.parent("ul").next("div").find("input:checked").each(function() {
				collection.get($(this).attr("value")).destroy({ success: function() { refreshList(collection); } });
			});
			target.parent("ul").next("div").children(".sub-info").empty();
		}
	},
	
	setContentHeight: function() {
		$("#content").css("height", this.$el.height() + 26 + "px");
	}
	
	

});

var DmuListItem = Backbone.View.extend({
	
	tagName: "li",
	
	className: "dmu-item",
	
	template: _.template($("#dmu-item-tmpl").html()),	
	
	render: function() {
		this.$el.html(this.template(this.model.toJSON().properties));
		return this;
	},
	
	events: {
		"click": "select"
	},
	
	select: function() {
		// Adjust CSS on the mapunit-list
		$("#mapunit-list").children().removeClass("selected-dmu");
		this.$el.toggleClass("selected-dmu");
		
		// Add the mapunit-info elements
		if (currentDmuInfo) { currentDmuInfo.undelegateEvents(); }		
		currentDmuInfo = new DmuInfo({ model: this.model, listItem: this });
		$("#mapunit-info").empty().append(currentDmuInfo.render().el);
		
		// Fetch related lithologies and render
		this.model.getLithologies({ success: this.addLithologies });
		
		// Fetch related events and preferred ages, render
		this.model.getGeologicHistory({ success: this.addEvents });
		this.model.getPreferredAge({ success: this.addPreferredAge });
		
		currentDmuInfo.setContentHeight();
	},
	
	addLithologies: function(liths, response) {
		$("#lith-list").empty();
		liths.each(function(lith) {
			var lithView = new LithListItem({ model: lith, id: "lith-item-" + lith.id });
			$("#lith-list").append(lithView.render().el);
			
			if ($("#lith-list").height() > $("#lith-info").height()) {
				$("#lith-info").css("height", $("#lith-list").height() + 8 + "px");
			} else {
				$("#lith-info").css("height", "");
			}
			currentDmuInfo.setContentHeight();
		});
	},
	
	addEvents: function(events, response) {
		$("#event-list").empty();
		events.each(function(event) {
			var ageView = new AgeListItem({ model: event, type: "event", id: "event-item-" + event.id });
			$("#event-list").append(ageView.render().el);
			
			if ($("#event-list").height() > $("#event-info").height()) {
				$("#event-info").css("height", $("#event-list").height() + 8 + "px");
			} else {
				$("#event-info").css("height", "");
			}
			currentDmuInfo.setContentHeight();
		});
	},
	
	addPreferredAge: function(ages, response) {
		$("#preferred-age-list").empty();
		ages.each(function(age) {
			var ageView = new AgeListItem({ model: age, type: "preferred-age", id: "age-item-" + age.id });
			$("#preferred-age-list").append(ageView.render().el);
			
			if ($("#preferred-age-list").height() > $("#preferred-age-info").height()) {
				$("#preferred-age-info").css("height", $("#preferred-age-list").height() + 8 + "px");
			} else {
				$("#preferred-age-info").css("height", "");
			}
			currentDmuInfo.setContentHeight();
		});
	}

});

var LithInfo = Backbone.View.extend({
	
	initialize: function(options) {
		this.listItem = options.listItem;
	},
	
	tagName: "div",
	
	className: "lith-info",
	
	template: _.template($("#lith-info-tmpl").html()),
	
	render: function() {
		var infoItem = this;
		this.$el.html(this.template(this.model.toJSON().properties));
		this.$el.find("input").each(function() {
			var vocab = application.vocabs.byName($(this).attr("vocab"));
			(new VocabularySelect({
				infoItem: infoItem,
				collection: vocab.terms,
				selected: $(this).attr("uri"),
				el: $(this)
			})).render();
		});
		return this;
	},
	
	onChange: function(event, ui) {
		this.model.set($(event.target).parent("td").parent(".lith-attr").attr("property"), ui.item.value);
		$(event.target).val(ui.item.label);
		this.model.save();
		this.listItem.render();
	}
});

var LithListItem = Backbone.View.extend({
	
	tagName: "li",
	
	className: "lith-item",
	
	template: _.template($("#lith-item-tmpl").html()),
	
	render: function() {
		var term = application.vocabularyLookup("SimpleLithology", this.model.get("lithology"));
		this.$el.html(this.template({ lithology: term, id: this.model.id }));
		return this;
	},
	
	events: {
		"click span": "select"
	},
	
	select: function() {
		$("#lith-list").children().removeClass("selected-lith");
		this.$el.toggleClass("selected-lith");
				
		lithView = new LithInfo({ model: this.model, listItem: this });
		$("#lith-info").empty().append(lithView.render().el);
	}
	
});

var AgeInfo = Backbone.View.extend({
	
	initialize: function(options) {
		this.type = options.type;
		this.className = this.type + "-info";
		this.listItem = options.listItem;
	},
	
	tagName: "div",
	
	template: _.template($("#event-info-tmpl").html()),
	
	render: function() {
		var infoItem = this;
		this.$el.html(this.template(this.model.toJSON().properties));
		this.$el.find("input").each(function() {
			var vocab = application.vocabs.byName($(this).attr("vocab"));
			(new VocabularySelect({
				infoItem: infoItem,
				collection: vocab.terms,
				selected: $(this).attr("uri"),
				el: $(this)
			})).render();
		});
		return this;
	},
	
	onChange: function(event, ui) {
		this.model.set($(event.target).parent("td").parent(".event-attr").attr("property"), ui.item.value);
		$(event.target).val(ui.item.label);
		this.model.save();
		this.listItem.render();
	}

});

var AgeListItem = Backbone.View.extend({
	
	initialize: function(options) {
		this.type = options.type;		
		this.className = this.type + "-item";
		this.list = $("#" + this.type + "-list");
		this.info = $("#" + this.type + "-info");
	},
	
	tagName: "li",
	
	template: _.template($("#event-item-tmpl").html()),
	
	render: function() {
		var term = application.vocabularyLookup("EventProcess", this.model.get("event"));
		this.$el.html(this.template({ event: term, id: this.model.id }));
		return this;
	},
	
	events: {
		"click span": "select"
	},
	
	select: function() {
		this.list.children().removeClass("selected-event");
		this.$el.toggleClass("selected-event");
		
		ageView = new AgeInfo({ model: this.model, type: this.type, listItem: this });
		this.info.empty().append(ageView.render().el);
	}
	
});

var VocabularySelect = Backbone.View.extend({
	
	initialize: function(options) {
		this.selected = options.selected;
		this.infoItem = options.infoItem;
	},
	
	render: function() {
		var terms = [];
		for (m in this.collection.models) {
			var model = this.collection.models[m];
			terms.push({ label: model.get("label"), value: model.get("uri") });
		}
		
		var infoItem = this.infoItem;
		this.$el.autocomplete({
			source: terms,
			select: function(event, ui) {
				infoItem.onChange(event, ui);
				return false;
			}
		});
		
		this.$el.val(application.vocabularyLookup(this.$el.attr("vocab"), this.selected));
		
		return this;
	}
});