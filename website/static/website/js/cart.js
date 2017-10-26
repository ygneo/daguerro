var cart_session_key = 'daguerro-cart'

$(document).ready(function() {
    $('div#selection a#cancel').live("click", function (e) {
        $.cookie(cart_session_key, null, { path: '/' });
        renderShoppingCart();
    });

    $("#ui-add-to-cart").click(function(e) {
            e.preventDefault();

            var current_item  = {'id': $(this).attr('data:item_id'),
                             'thumb_url': $(this).attr('data:item_thumb_url'),
                             'title': $(this).attr('data:item_title')
            };
            var items = JSON.parse($.cookie(cart_session_key));

            if (items) {
                items[current_item.id] = current_item;
            }
            else {
                items = new Object();
                items[current_item.id] = current_item;
            }

            $.cookie(cart_session_key, null);
            $.cookie(cart_session_key, JSON.stringify(items), {expires: null,  path: "/"});

            renderShoppingCart();
     });

    $("#ui-shopping-cart-make-request").live("click", function(e) {
            $(this).hide();
            $(shopping_cart_container_id + " table tr td input[type=checkbox]:not(:checked)").each(function() {
                    $(this).parent("td").each(function() {
                            $(this).parent("tr").fadeOut();
                    });
            });
            $("fieldset#request-form").show();
        });

    $("fieldset#request-form input, fieldset#request-form textarea").live("focus", function() {
            if($(this).val()==$(this).attr("data:default")) {
                $(this).val("");
            }
        });
    $("fieldset#request-form input[type=text], fieldset#request-form textarea").live("blur", function() {
            if($(this).val()=="")
                {
                    $(this).val($(this).attr("data:default"));
                }
        });

    function validEmail(email) {
	    var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
	    if( !emailReg.test( email ) ) {
		    return false;
	    } else {
		    return true;
	    }
    }

    $("#shopping-cart-submit").live("click", function(e) {
        input_email = $("input[name=email]")
        if (!validEmail(input_email.attr("value"))) {
            e.preventDefault();
	        input_email.qtip({
	            content: gettext("You must enter a valid e-mail"),
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
	            show: { ready: true, },
	            hide: { when: { target: input_email,
			                    event: 'keyup'
			                  },
		                effect: { type: 'fade' }
		              },
	        });
        }
    });



});


function renderShoppingCart() {
    var cart = $('div#selection');
    var show_cart = !$("form#photos_request").length;

 
    photo_items = Array();
    current_object = Object();
    var items = JSON.parse($.cookie(cart_session_key), function (key, value) {
	       if (typeof value === 'string') {
		        if (key == 'id') {
			        current_object = Object();
			        current_object.id = value;
		        }
		        else if (key == 'thumb_url') {
			        current_object.thumb_url = value;
		        }
		        else if (key == 'title') {
			        current_object.title = value;
			        photo_items.push(current_object);
		        }
	        }
    });

    cart.html('');
    cart.hide();

    if (photo_items.length && show_cart) {
        cart.html('<ul id="photos"></ul>');
        var list = $("ul#photos");

        photo_items.forEach(function (photo, id) {
                list.append('<li><img src="'+ photo.thumb_url + '" alt="' + photo.title + 'title="' + photo.title + '"/><p>' + photo.title  + '</p>');
    	});

        cart.append('<div id="buttons"><a id="request" href="/request">Solicitar estas fotografías</a><a id="cancel">Cancelar</a></div>');

        cart.show();
    }

}

//This prototype is provided by the Mozilla foundation and
//is distributed under the MIT license.
//http://www.ibiblio.org/pub/Linux/LICENSES/mit.license

if (!Array.prototype.forEach)
{
  Array.prototype.forEach = function(fun /*, thisp*/)
  {
    var len = this.length;
    if (typeof fun != "function")
      throw new TypeError();

    var thisp = arguments[1];
    for (var i = 0; i < len; i++)
    {
      if (i in this)
        fun.call(thisp, this[i], i, this);
    }
  };
}
