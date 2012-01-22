$(function() {
        var search_term = $.getQueryParam("term");
        if (search_term == undefined) {
            var default_search_value = $("#buttons #search input#term").attr("value");
        }

        $("#buttons #search input#term").focusin( function() {
                if (search_term == undefined && $(this).attr("value") == default_search_value) {
                    $(this).attr("value", "");
                    $(this).addClass("active");
                }
            });
        $("#buttons #search input#term").focusout( function() {
                if ($(this).attr("value") == "") {
                    $(this).attr("value", "Buscar fotografías");
                    default_search_value = $(this).attr("value");
                    $(this).removeClass("active");
                    search_term = undefined;
                    console.log(search_term);
                }
            });
});

// jQuery getQueryParam Plugin 1.0.0 (20100429)
// By John Terenzio | http://plugins.jquery.com/project/getqueryparam | MIT License
(function($){$.getQueryParam=function(param){var pairs=location.search.substring(1).split('&');for(var i=0;i<pairs.length;i++){var params=pairs[i].split('=');if(params[0]==param){return params[1]||'';}}return undefined;};})(jQuery);