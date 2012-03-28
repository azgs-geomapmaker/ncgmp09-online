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
			} else {
				console.log("Fail!!");
			}
		}
	});
}