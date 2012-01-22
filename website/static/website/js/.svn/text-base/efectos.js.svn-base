$(document).ready(function() {
    // Category effects
    $("#category").corner();
    $("#menu div.mini").corner();

    // Gallery effects
    $("#gallery li, #subgallery li,").corner("br bl");
    $("span#num_photos").corner();

    // Photo gallery efects
    $("#photos ul li div.photo").corner();


    $("form#search input#query").focusin( function() {
            if ($(this).val() == $(this).attr("data:default")) {
                $(this).val("");
                $(this).addClass("active");
            }
        });
    $("form#search input#query").focusout( function() {
            if ($(this).val() == "") {
                $(this).val($(this).attr("data:default"));
                $(this).removeClass("active");
            }
        });
});
  
// jQuery getQueryParam Plugin 1.0.0 (20100429)
// By John Terenzio | http://plugins.jquery.com/project/getqueryparam | MIT License
(function($){$.getQueryParam=function(param){var pairs=location.search.substring(1).split('&');for(var i=0;i<pairs.length;i++){var params=pairs[i].split('=');if(params[0]==param){return params[1]||'';}}return undefined;};})(jQuery);
