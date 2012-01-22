var cart_session_key = 'daguerro-cart' 

$(document).ready(function() {
    var shopping_cart_container_id = 'div#shopping-cart';

    $('a#open-shopping-cart').qtip({
            content: renderShoppingCart(),
                position: {
                corner: {
                    target: 'bottomMiddle',
                    tooltip: 'topMiddle'
                        }
            },
                style: { 
                width: 220,
                    padding: 5,
                    background: 'white',
                    color: 'black',
                    'font-size': 'small',
                    border: {
                    width: 1,
                        radius: 4,
                        color: 'white'
                        },
                    textAlign: 'left',
                    tip: 'topMiddle',
                    name: 'dark'
                    },
                fixed: true,
               hide: { when: { target: $("a#close-shopping-cart"), event: "doubleclick" }},  
               show: { when: { event: "click" }}
    });

    $('a#open-shopping-cart').click(function (e) { 
            e.preventDefault(); 
            e.stopPropagation();
            renderShoppingCartTable(shopping_cart_container_id);
            $('a#open-shopping-cart').qtip("show");
            $("fieldset#request-form").hide();
            $("#ui-shopping-cart-make-request").show();
        });

    $('a#close-shopping-cart').live("click", function (e) { 
            $('a#open-shopping-cart').qtip("hide");
            });

    $("#ui-add-to-cart").click(function(e) {
            e.preventDefault();
            current_item  = {'id': $(this).attr('data:item_id'),
                             'thumb_url': $(this).attr('data:item_thumb_url'),
                             'title': $(this).attr('data:item_title')
            };
            items = JSON.parse($.cookie(cart_session_key));
            if (items) {
                items[current_item.id] = current_item;
            }
            else {
                items = new Object();
                items[current_item.id] = current_item;
            }
            $.cookie(cart_session_key, null);
            $.cookie(cart_session_key, JSON.stringify(items), {expires: null,  path: "/"});
            updateShoppingCartNumItems();
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
    
   

});

function renderShoppingCartTable(container_id) {
    table = $("table#shopping-list");
    table.html('');
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
    photo_items.forEach(function (photo, id) {
        table.append('<tr><td><input type="checkbox" checked="checked" class="select-item"/><input type="hidden" name="shopping-cart-items[]" value ="' + photo.id + '" /><td><img src="'+ photo.thumb_url + '" alt="' + photo.title + 'title="' + photo.title + '"/></td><td>' + photo.title  + '</td></tr>');
	});
 }

function renderShoppingCart() {
    updateShoppingCartNumItems();
    return $('<div id="shopping-cart"><div id="head"><h3>Cesta de fotografías</h3><a id="close-shopping-cart" href="#" title="Close">x</a></div><form action="/solicitar-fotos/" method="post"><table id="shopping-list"></table><input id="ui-shopping-cart-make-request" type="button" value="Solicitar"></input><fieldset id="request-form"><input type="text" name="email" value="tu correo electrónico" data:default="tu correo electrónico"/><textarea name="message" rows="5" data:default="tus comentarios (opcional)">tus comentarios (opcional)</textarea><input type="hidden" name="redirect_to_url" value="' + window.location + '"/><input type="submit" value="Enviar solicitud"/></fieldset></form></div>');
 }

function numItemsInShoppingCar() {
    var count=0;
    var items = JSON.parse($.cookie(cart_session_key));
    for (key in items) { count++; }
    return count;
}

function updateShoppingCartNumItems() {
    var num_items = numItemsInShoppingCar();
    if (num_items > 0) {
        $("#tools #shop").show();
        $("#shopping-cart-num-items").html(num_items);
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

 
