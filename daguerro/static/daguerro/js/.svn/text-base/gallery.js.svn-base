$(function() {
        if ($("ul#categories li").length) {
            $("ul#categories li").droppable({
                    accept: "ul#photos li",
                        tolerance: "pointer", 
                        drop: function(event, ui) {
                        $(this).addClass( "ui-state-highlight" )
                            ui.draggable.fadeOut("slow");
                        gal_id = $(this).attr("id").split("_")[1];
                        photo_id = ui.draggable.attr("id").split("_")[1];
                        $.post("/daguerro/gallery/"+ gal_id + "/add-photo/" + photo_id);
                    },
                        over: function(even, ui) {
                        $(this).children('div.overlap-droppable').toggleClass("overlap-droppable-active");
                        $(this).children('div.overlap-droppable').css("opacity", "0.8");
                    },
                        out: function(even, ui) {
                        $(this).children('div.overlap-droppable').toggleClass("overlap-droppable-active");
                    },
            });
        }

        if ($(".sortable").length) {
            $(".sortable") .sortable({
                    placeholder: "placeholder",
                        opacity: 0.7,
                        scroll: true,
                        tolerance: "pointer",
                        update: function(event, ui) {
                        ul_id = ui.item.parent("ul").attr("id");
                        order = $("#" + ul_id).sortable('serialize'); 
                        if (ul_id == 'categories') {
                            item_type = 'gallery'
                                }
                        else if (ul_id == 'photos') {
                            item_type = 'photo'
                                }
                        $.post("/daguerro/sort-items", order + "&item_type=" + item_type);
                    },            
                        start: function(even, ui) {
                        if ($(this).attr("id").indexOf("photo") === 0) {
                            overlap = $('<div class="overlap-droppable"></div>');
                            overlap.prependTo('ul#categories li');
                            $('div.overlap-droppable').css("opacity", 0.7); 
                        }
                    },
                        stop: function(even, ui) {
                        $('div.overlap-droppable').remove();
                    },
              });
              $( ".sortable" ).disableSelection();
        }
 });



