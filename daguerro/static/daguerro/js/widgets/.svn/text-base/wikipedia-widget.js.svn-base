(function($) {

    $.wikipediaWidgetOptions = {
        appendTo: null,
        searchLang: 'es',
        urlField: null,
    };

    var wikipediaSearch = function(query, result_found, link, current_link) {
        result_found.hide();
        if (query)  {
            $.ajax({
				url: 'http://' + $.wikipediaWidgetOptions.searchLang + 
                        '.wikipedia.org/w/api.php?action=query&format=json&prop=langlinks&callback=?',
				dataType: 'json',
				data: { titles: query },
				success: function(data) {
                        for (pageid in data.query.pages) break;
                        if (pageid != -1) {
                            url = 'http://' + $.wikipediaWidgetOptions.searchLang + '.wikipedia.org/wiki/' + escape(data.query.pages[pageid].title);
                            link.attr("href", url);
                            result_found.show();
                            current_link.hide();
                        }
				}	
			});
        }
    }

    var toggleCurrentLink = function(urlField, current_link) {
        if (urlField.val() != '') { 
            current_link.children("a.ui-wikipedia-link").attr("href", urlField.val());
            current_link.show();
        }
        else {
            current_link.hide();
        }
    }        


    $.fn.wikipediaWidget = function(settings) {

        $.extend($.wikipediaWidgetOptions, settings);

        return this.each(function() {
                var input = $(this);
                var widget = $(this).next(".ui-wikipedia-widget");
                var result_found = widget.children(".ui-wikipedia-result-found");
                var current_link = widget.children(".ui-wikipedia-current-link");
                var link = result_found.children("a.ui-wikipedia-link");
                var actions = result_found.children(".ui-wikipedia-link-actions");
                var urlField = $("input#" + $.wikipediaWidgetOptions.urlField);
                
                toggleCurrentLink(urlField, current_link);
                if ($.wikipediaWidgetOptions.insertAfter) {
                    $(this).next(".ui-wikipedia-widget").
                        appendTo($.wikipediaWidgetOptions.insertAfter);
                }
                                
                if (urlField.val() == '') { 
                    wikipediaSearch(input.val(), result_found, link, current_link);
                }
                
                input.keyup(function () { 
                        console.log("key-up-search");
                        wikipediaSearch($(this).val(), result_found, link, current_link);
                    });

                actions.children(".ui-wikipedia-link-yes").click(function () { 
                        urlField.val(link.attr("href"));
                        result_found.hide();
                        toggleCurrentLink(urlField, current_link);
                    });
                actions.children(".ui-wikipedia-link-no").click(function () { 
                        urlField.val('');
                        result_found.hide();
                    });
                
                current_link.children(".ui-wikipedia-link-actions").children("a.ui-wikipedia-unlink")
                    .click(function () { 
                        urlField.val('');
                        toggleCurrentLink(urlField, current_link);
                    });

        });
    };

})(jQuery);
