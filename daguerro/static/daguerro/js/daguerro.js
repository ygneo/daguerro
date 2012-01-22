$(function() {
        $(".ui-delete-button").live("click", function(e) {
                if (!confirm("¿Estás seguro de que quieres borrarlo?")) {
                    e.preventDefault();
                }
            });
        
        $(".ui-delete-button-bulk").live("click", function(e) {
                if (!confirm("¿Estás seguro de que quieres aplicar esa acción a todos los elementos seleccionados?")) {
                    e.preventDefault();
                }
            });


});



