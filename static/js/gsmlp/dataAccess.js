define(["dojo/query", "dojo/_base/xhr"], function(query, xhr) {
	var dataAccess = {
		
		getMapUnits: function(gmId, callback) {
			xhr.get({
				url: "/ncgmp/geomap/" + gmId + "/mapunits/",
				handleAs: "json",
				load: callback
			});
		}
			
	};
	
	return dataAccess;
});