$(document).ready(function() {
    $("<div id='ui-open-galleries'>").insertBefore($('fieldset#galleries label:not(fieldset#galleries ul label)'));

    $('fieldset#galleries-fields input[type=checkbox]').each(function(index) {
	    subtree = $(this).nextAll("ul");
	    if (subtree.length) {
	        $('<div id="ui-tree-node-handler" class="open-node"></div>').insertBefore($(this));
	    }
	    else {
	        $(this).parent("li").css("margin-left", "14px");
	    }
    });

    $('fieldset#galleries-fields li ul').children().hide();

    offset = 31;
    form_width = parseInt($("form#search").css("width"));
    options_padding = 24;


    function toggle_search_options(force_hide) {
        force_hide = typeof force_hide !== 'undefined' ? force_hide : false;
        button = $('input#search_options_button');
	    button_offset = button.offset();
	    $("#search_options").css("top",button_offset.top + offset);
        if (force_hide) {
            $("#search_buttons").removeClass("active");
            button.removeClass("active");
	        $("#ui-arrow-down").hide();
	        $("#search_options").hide();
        }
        else {
            $("#search_buttons").toggleClass("active");
	        button.toggleClass("active");
	        $("#ui-arrow-down").toggle();
	        $("#ui-arrow-down").offset({top: button_offset.top + offset - 1, 
				                        left: button_offset.left - (offset / 10)
				                       });
	        $("#search_options").toggle();

        }
    }

    $('html').click(function() {
	if ($("#search_options").length) {
            toggle_search_options(force_hide=true);
	}
    });

    $('#search_options').click(function(e) {
        e.stopPropagation();
    });

    $('input#search_options_button').click(function (e) {
        e.stopPropagation();
        toggle_search_options();
    });
    
    $('#search_in_galleries_1').click(function (e) {
	    $("div#galleries ul").show();
    });

    $('#search_in_galleries_0').click(function (e) {
	    hide_qtips();
	    $("div#galleries ul").hide();
    });

    $('#ui-tree-node-handler.open-node').click(function (e) {
	    $(this).toggleClass("close-node");
	    $(this).nextAll("ul").children().toggle();
    });

    $('#ui-open-galleries, #ui-open-galleries + label').click(function (e) {
	    $("#ui-open-galleries").toggleClass("active");
	    $("fieldset#galleries-fields > ul").toggle();
    });

    $('div#galleries input[type=checkbox]').click(function (e) {
	    if ($(this).is(':checked')) {
	        $(this).nextAll("ul").find("input").attr("checked", true);
	    }
	    else {
	        $(this).nextAll("ul").find("input").attr("checked", false);
	    }

    });


    function show_qtip(target, message) { 
	    target.qtip({
	        content: gettext(message),
	        position: {
		        corner: {
		            target: 'bottomLeft',
		        },
	        },
	        style: { 
		        tip: {
		            corner: 'topMiddle',
		            color: '#58880C',
		            size: {
			            x: 20,
			            y: 8
		            },
		        },
		        background: "#58880C",
		        color: "white",
		        border: {
		            width: 0,
		            radius: 4,
		            color: "#58880C",
		        },
		        'font-size': 'small',
	        },
	        show: { ready: true, 
		            when: { target: $('.ui-search-button'),
			                event: 'click'
			              },
		          },
	        hide: { when: { target: target,
			                event: 'keyup'
			              },
		            effect: { type: 'fade' } 
		          },
	    });
    }

    
    function no_galleries_selected() {
	    return ($("#search_in_galleries_1").is(':checked') && $("#galleries-fields input[type=checkbox]:checked").length == 0);
    }

    function hide_qtips() {
	    $(".qtip").each(function() {
	        $(this).qtip("destroy");
	    });
    }


    $('.ui-search-button').click(function(event) {
	    hide_qtips();
	    var error_message = "";
	    if ($("input#query").val() == "") {
	        error_message = gettext("You must enter a query");
	        target = $("input#query");
	    }
	    else if (no_galleries_selected()) {
	        error_message = gettext("You must choose at least one gallery");
	        target = $("#search_in_galleries_1");
	    }

	    if (error_message) {
	        event.preventDefault();
	        show_qtip(target, error_message);
	    }
	    else {
	        if ($("#search_in_galleries_0").is(':checked')) {
		        $("#galleries-fields input[type=checkbox]:checked").attr("checked", false);
	        }
	    }
    });

    $("input#query").bind("keyup", "mouseover", hide_qtips());

    $("#galleries ul li").live("mouseover", function () {
	    hide_qtips();
    });

});

