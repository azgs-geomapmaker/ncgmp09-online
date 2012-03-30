function loadData(id) {
	var csrf = $("#csrf").val();
	
	$("#waiting").toggleClass("hidden");
	
	$.ajax({
		url: "is_loaded/",
		type: "put",
		data: { value: true },
		dataType: "json",
		headers: { "X-CSRFToken": csrf },
		success: function(response) {
			if (response.success) {
				window.location.reload();
			} 
		},
		error: function(xhr) {
			if (xhr.status === 500) {
				var message = xhr.responseText.match(/Exception Value: .+\n/)[0].replace(/Exception Value: /, "");
				$("#waiting").toggleClass("hidden");
				$("body").append("<p><strong>An error occurred while loading data: </strong></p>");
				$("body").append("<p>" + message + "</p>");
			}
		}
	});
}