var cart_session_key = 'daguerro-cart'


function renderPhotosTable() {
    var table = $('table#photos_list');

    table.html('');

    photo_items = Array();
    current_object = Object();
    JSON.parse($.cookie(cart_session_key), function (key, value) {
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

    if (photo_items.length) {
        photo_items.forEach(function (photo, id) {
            var img = '<img src="'+ photo.thumb_url + '" alt="' + photo.title + 'title="' + photo.title + '"/>';
            var title = '<div>' + photo.title + '</div>'
            var button = '<button class="remove" data:id="' + photo.id + '">Quitar</button>'
            var input = '<input type="hidden" name="photo_ids[]" value ="' + photo.id + '"/>'

            table.append('<tr><td>' + img + '<td><td>' +  title + button + input + '</td></tr>');
    	});

    }
}

$('#photos_list button.remove').live("click", function (e) {
	e.preventDefault();

	var items = JSON.parse($.cookie(cart_session_key));

	delete items[$(this).attr("data:id")];

	if (Object.keys(items).length === 0) {
		window.location = "/";
	}

	$.cookie(cart_session_key, null);
  $.cookie(cart_session_key, JSON.stringify(items), {expires: null,  path: "/"});

	renderPhotosTable();
});


renderPhotosTable();
