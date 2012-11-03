$(function() {
		var use_search_cache = false,
            search_cache = {},
			lastXhr;
        

        $("#photo-related #change-photo-fs input").focus(function(event) { 
                $(this).prevAll("input[type=radio]").eq(0).attr("checked", "checked");
            });

        if ($("#photo-related #change-photo-fs input#photo-title").length) {
                $("#photo-related #change-photo-fs input#photo-title").autocomplete({
                        minLength: 3,
                        appendTo: "#photo-related #change-photo-fs #photo_results",
                        source: function(request, response) {               
                                var term = request.term;
                                if (use_search_cache && term in search_cache) {
                                    response(search_cache[term]);
                                    return;
                                }
			    url = resolve("daguerro-search-photo-ajax", {format: "json"})
                            lastXhr = $.getJSON(url, request, function(data, status, xhr) {
                                        if (use_search_cache) {
                                            search_cache[term] = data;
                                        }
                                        if (xhr === lastXhr) {
                                            console.log(data);
                                            response(data);
                                        }
                                    });
                            },
                        select: function(event, ui) { 
                            $("input[name=id_photo]").val(ui.item.id);
                            $("#photo img").attr("src", ui.item.image);
                        },
                        open: function(event, ui) { 
                            $("#photo_results").addClass("active");
                        },
                        close: function(event, ui) { 
                            $("#photo_results").removeClass("active");
                        },
                    })
                    .data("autocomplete")._renderItem = function(ul, item) {
                    return $("<li></li>")
                    .data("item.autocomplete", item )
                    .append(item.label)
                    .appendTo(ul);
                };
         }

        $("#photo-related #change-photo-fs input#photo-title").focusin(function(event) { 
                if ($(this).hasClass('inactive')) {
                    if ($(this).attr('rel') == undefined) {
                        $(this).attr('rel', $(this).val());
                    }
                    $(this).val('');
                    $(this).removeClass('inactive');
                }
            });

        $("#photo-related #change-photo-fs input#photo-title").focusout(function(event) { 
                if ($(this).val() == '') {
                    $(this).val($(this).attr('rel'));
                    $(this).addClass('inactive');
                }
            });


});

