$(document).ready(function() {
    $("<div id='ui-arrow-down'>").insertAfter($('input#search_options_button'));
    $("<div id='ui-open-galleries'>").insertBefore($('fieldset#galleries label:not(fieldset#galleries ul label)'));
    $('fieldset#galleries input[type=checkbox]').each( function( index ) {
	$('<div id="ui-tree-node-handler" class="open-node"></div>').insertBefore($(this));
    });

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

    $('#ui-open-galleries, #ui-open-galleries + label').click(function (e) {
	$("#ui-open-galleries").toggleClass("active");
	$("hr#ui-separator").toggle();
	$("fieldset#galleries > ul").toggle();
    });

});
