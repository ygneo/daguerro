$(function() {

    $(".ui-delete-photo-button").live("click", function(e) {
	e.preventDefault();
	$('#delete-photo-modal').modal();
	$("#delete-photo-modal .btn-danger").attr("data:url", $(this).attr("href"));
    });

    $("#delete-photo-modal .btn-danger").live("click", function(e) {
	$('#delete-photo-modal').modal('hide');
	window.location.replace($(this).attr("data:url"));
    });


    $(".ui-delete-gallery-button").live("click", function(e) {
        e.preventDefault();
	slugs = $(this).attr("data:gallery_slugs")
	$("#delete-gallery-modal .btn-danger").attr("data:gallery_slugs", slugs);
	$('#delete-gallery-modal').modal({
	    remote: dutils.urls.resolve('daguerro-gallery-delete-intent', {slugs: slugs})
	});
    });
    
    $(".ui-delete-button-bulk").live("click", function(e) {
        if (!confirm("¿Estás seguro de que quieres aplicar esa acción a todos los elementos seleccionados?")) {
            e.preventDefault();
        }
    });

    $("#delete-gallery-modal .btn-danger").live("click", function(e) {
	$('#delete-gallery-modal').modal('hide');
	slugs = $(this).attr("data:gallery_slugs");
	window.location.replace(dutils.urls.resolve('daguerro-gallery-delete', {slugs: slugs}));
    });

    $("input[name=is_public]").change(function() {
	if (typeof $(this).data("was_checked") == "undefined") {
	    $(this).data("was_checked", !this.checked);
	}
	$(".ui-save-gallery-button").data("publish_status_changed", this.checked != $(this).data('was_checked'));
    });

    $(".ui-save-gallery-button").live("click", function(e) {
	if ($(this).data("publish_status_changed")) {
	    e.preventDefault();
	    $("#save-gallery-modal").modal();
	}
    });

    $("#save-gallery-modal .btn-danger").live("click", function(e) {
	$('#save-gallery-modal').modal('hide');
	$('form#gallery').unbind("submit").submit();
    });

});



