$(document).ready(function() {
    $("<div id='ui-arrow-down'>").insertAfter($('input#search_options_button'));

    $("<div id='ui-open-galleries'>").insertBefore($('fieldset#galleries label:not(fieldset#galleries ul label)'));

    $('fieldset#galleries input[type=checkbox]').each(function(index) {
	subtree = $(this).nextAll("ul");
	if (subtree.length) {
	    $('<div id="ui-tree-node-handler" class="open-node"></div>').insertBefore($(this));
	}
	else {
	    $(this).parent("li").css("margin-left", "14px");
	}
    });

    $('fieldset#galleries li ul').children().hide();
    $("#search_in_galleries_0").attr("checked", true);

    offset = 31;
    form_width = parseInt($("form#search").css("width"));
    options_padding = 24;

    $('input#search_options_button').click(function (e) {
	button_offset = $(this).offset();
	$(this).toggleClass("active");
	$("#ui-arrow-down").toggle();
	$("#ui-arrow-down").offset({top: button_offset.top + offset - 1, 
				    left: button_offset.left - (offset / 10)
				    });
	$("#search_options").toggle();
	$("#search_options").css("width", form_width - options_padding);
	$("#search_options").offset({top: button_offset.top + offset, 
				     left: button_offset.left - $("#seach_options").css("width")
				    });

    });

    $('#search_in_galleries_1').click(function (e) {
	$("div#galleries ul").show();
    });

    $('#search_in_galleries_0').click(function (e) {
	$("div#galleries ul").hide();
    });

    $('#ui-tree-node-handler.open-node').click(function (e) {
	$(this).toggleClass("close-node");
	$(this).nextAll("ul").children().toggle();
    });

    $('#ui-open-galleries, #ui-open-galleries + label').click(function (e) {
	$("#ui-open-galleries").toggleClass("active");
	$("fieldset#galleries > ul").toggle();
    });

    $('div#galleries input[type=checkbox]').click(function (e) {
	if ($(this).is(':checked')) {
	    $(this).nextAll("ul").find("input").attr("checked", true);
	}
	else {
	    $(this).nextAll("ul").find("input").attr("checked", false);
	}

    });

    $('.ui-search-button').click(function(event) {
	if ($("input#query").val() == "") {
	    event.preventDefault();
	    $("input#query").qtip({
		content: gettext("You must enter a query"),
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
		        target: $(this)
		      },
		hide: { when: { target: $(this),
				event: 'mouseout'
			      },
			effect: { type: 'fade' } 
		      }
	    });
	}
    });


    $("input#query").mouseover(function() { $(this).qtip("destroy"); });

});
