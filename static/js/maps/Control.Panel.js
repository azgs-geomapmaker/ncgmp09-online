function refreshLegend(event) {
	var map = this;
	map.activePanel.updateContent();
}

L.Control.Panel = L.Control.extend({
	initialize: function(options) {
		L.Control.prototype.initialize.call(this, null, options);
		L.Util.setOptions(this, options);
		
		this.urlContentTemplate = new JadeContent("/static/templates/legend-template.jade");
	},
	
	onAdd: function(map) {
		map.activePanel = this;		
		this._initLayout();
		this.updateContent();
		
		map.on("moveend", refreshLegend);
		map.on("zoomend", refreshLegend);
		
		return this._container;
	},
	
	updateContent: function() {
		var template = this.urlContentTemplate;
		var title = this.options.title || "Geologic Map"
		var container = this._container;		
		var bounds = this._map.getBounds().toBBoxString();		
		$.get(this.options.url + "?bbox=" + bounds, function(response) {
			dmus = [];
			for (f in response.features) {
				dmus.push({
					id: response.features[f].id,
					color: "rgba(" + response.features[f].properties.areafillrgb.replace(/;/g, ",") + ",1)",
					label: response.features[f].properties.label,
					name: response.features[f].properties.name,
					description: response.features[f].properties.description
				});
			}
			container.innerHTML = template.generateContent({ properties: { dmus: dmus, title: title } });			
		}, "json");
	},
	
	_initLayout: function() {
		var mapHeight = this._map.getSize().y;
		var panelWidth = this.options.width || 200;
		var panelId = this.options.id || 'panel-control';
		
		this._container = L.DomUtil.create('div', 'panel-control');
		this._container.id = panelId;
		this._container.style.height = mapHeight + "px";
		this._container.style.width = panelWidth + "px";
		this._container.style.margin = "0px";
		
		if (!L.Browser.touch) {
			L.DomEvent.disableClickPropagation(this._container);
		} else {
			L.DomEvent.addListener(this._container, 'click', L.DomEvent.stopPropagation);
		}
	}
	
});