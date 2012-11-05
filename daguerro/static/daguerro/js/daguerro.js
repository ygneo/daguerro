$(function() {
    $(".ui-delete-button").live("click", function(e) {
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

});



