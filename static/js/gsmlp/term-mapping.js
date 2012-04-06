require(["gsmlp/dataAccess"], function(data) {
	data.getMapUnits(geomapId, function(data) {
		console.log(data);
	});
});