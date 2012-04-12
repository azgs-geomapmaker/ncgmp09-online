function showErrors(error) {
	error = JSON.parse(error.replace(/&quot;/g, '"').replace(/&gt;/g, '>'));
	var errorEle = $("#errors");
	
	if (error.hasOwnProperty("MissingTables")) {
		errorEle.append("<h2>Missing required Tables:</h2><ul></ul>");
		error.MissingTables.forEach(function(tableName) {
			errorEle.children("ul").append("<li><strong>" + tableName + "</strong></li>");
		});
	}
	
	if (error.hasOwnProperty("MissingFields")) {
		errorEle.append("<h2>Missing required fields as indicted in the following tables:</h2><ul></ul>");
		for (var tableName in error.MissingFields) {
			errorEle.children("ul").append("<li><strong>" + tableName + ":</strong> " + error.MissingFields[tableName].join(", ") + "</li>");
		}
	}
	
	if (error.hasOwnProperty("RepeatedUniqueValues")) {
		errorEle.append("<h2>Values are repeated in the following fields that are required to be unique:</h2><ul></ul>");
		for (var tableName in error.RepeatedUniqueValues) {
			errorEle.children("ul").append("<li id='id_" + tableName + "'><strong>" + tableName + ":</strong><ul></ul>");
			for (var fieldName in error.RepeatedUniqueValues[tableName]) {
				$("#id_" + tableName).children("ul").append("<li id='id_" + fieldName + "'>" + fieldName + ":<ul></ul>");
				error.RepeatedUniqueValues[tableName][fieldName].forEach(function(value) {
					$("#id_" + fieldName).children("ul").append("<li>" + value + "</li>");
				});
			}
		}		
	}
	
	if (error.hasOwnProperty("MissingForeignKeys")) {
		errorEle.append("<h2>Foreign keys in the following tables do not point to a valid record in the related table:</h2><ul></ul>");
		for (var tableName in error.MissingForeignKeys) {
			errorEle.children("ul").append("<li id='id_" + tableName + "'><strong>" + tableName + ":</strong><ul></ul>");
			for (var fieldToTable in error.MissingForeignKeys[tableName]) {
				var fieldToTableId = fieldToTable.replace(/ >> /, "-");
				$("#id_" + tableName).children("ul").append("<li id='id_" + fieldToTableId + "'>" + fieldToTable + ":<ul></ul>");
				error.MissingForeignKeys[tableName][fieldToTable].forEach(function(value) {
					$("#id_" + fieldToTableId).children("ul").append("<li>" + value + "</li>");
				});
			}
		}
	}
}

$(document).ready(function() {
	$(".gm-id").each(function() {
		var id = $(this).html().replace(/^\s+|\s+$/g, "");
		$(this).next("a").attr("href", id + "/");
	});
});