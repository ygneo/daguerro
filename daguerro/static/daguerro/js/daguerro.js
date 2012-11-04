$(function() {
    $(".ui-delete-button").live("click", function(e) {
        e.preventDefault();
	gallery_slugs = $(this).attr("data:gallery_slugs")
	$("#delete-gallery-modal .btn-primary").attr("data:gallery_slugs", gallery_slugs);
	$('#delete-gallery-modal').modal();
    });
    
    $(".ui-delete-button-bulk").live("click", function(e) {
        if (!confirm("¿Estás seguro de que quieres aplicar esa acción a todos los elementos seleccionados?")) {
            e.preventDefault();
        }
    });


    $("#delete-gallery-modal .btn-primary").live("click", function(e) {
	$('#delete-gallery-modal').modal('hide');
	slugs = $(this).attr("data:gallery_slugs");
	window.location.replace(dutils.urls.resolve('daguerro-gallery-delete', {slugs: slugs}));
    });

});



