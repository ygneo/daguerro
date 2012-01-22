$(document).ready(function(){
        var map_id = "map_canvas";
        var mapOptions = {
            zoom : 10,
            mapTypeId: google.maps.MapTypeId.ROADMAP,
        };
        var map = new google.maps.Map(document.getElementById(map_id),mapOptions);
        var geocoder = new google.maps.Geocoder();
        var current_marker;

        google.maps.Map.prototype.clearMarkers = function() {
            for(var i=0; i < this.markers.length; i++){
                this.markers[i].setMap(null);
            }
            this.markers = new Array();
        };


        function hideMap() {
            $("#" + map_id).css('visibility', 'hidden');
            $("#map_canvas").css('z-index', '-1');
            $("#map_canvas").css('position', 'absolute');

        }

        function showMap() {
            $("#map_canvas").css('visibility', 'visible');
            $("#map_canvas").css('z-index', '1');
            $("#map_canvas").css('position', 'relative');
        }
        
        function setMap(latlng) {
            showMap();
            setLocationFields(latlng);
            if (current_marker) {
                current_marker.setMap(null);
            }
            current_marker = new google.maps.Marker({
                    map:map,
                    draggable:true,
                    animation: google.maps.Animation.DROP,
                    position: latlng,
                    title: $("#map_canvas").attr("data-tooltip-title"),
                });

            google.maps.event.addListener(current_marker, 'dragend', function(event) {
                    setLocationFields(event.latLng);
                });
            map.setCenter(latlng);
        }

        function setLocationFields(latlng) {
            if (latlng) {
                lat = latlng.lat();
                lng = latlng.lng();
            }
            else {
                lat = lng = ""
            }
            $("#id_latitude").val(lat);
            $("#id_longitude").val(lng);
        }


        if ($("#id_latitude").val() && $("#id_longitude").val()) {
            setMap(new google.maps.LatLng($("#id_latitude").val(), $("#id_longitude").val()));
            $(".no_location").show();
        }
        else {
            hideMap();
        }
        $(".gmaps_location").autocomplete({
                appendTo: "#map_results",
                source: function(request, response) {
                    if (request.term == '') {
                        hideMap();
                        setLocationFields(null);
                        $("label .no_location").hide();
                    }
                    else {
                        $(".gmaps_location").next(".help_text").hide();
                        $("#no_map_results").hide();
                        geocoder.geocode( {'address': request.term, 'language': 'es_ES' }, 
                                          function(results, status) { 
                                              if (status == google.maps.GeocoderStatus.OK) {
                                                  lat = results[0].geometry.location.lat();
                                                  lng = results[0].geometry.location.lng();
                                                  latlng = new google.maps.LatLng(lat, lng);
                                                  response($.map(results, function(loc) {
                                                              return {
                                                                      label: loc.formatted_address,
                                                                      value: loc.formatted_address,
                                                                      bounds: loc.geometry.bounds,
                                                                      latlng:  loc.geometry.location,
                                                                     }
                                                          }));
                                              }
                                              else if (status == google.maps.GeocoderStatus.ZERO_RESULTS) {
                                                  hideMap();
                                                  $("#no_map_results").show();
                                                  setLocationFields(null);
                                                  response({});
                                              }
                                          })
                            }
                        },
                    select: function(event, ui) {
                        var bounds = ui.item.bounds;
                        setMap(ui.item.latlng);
                        $(".no_location").show();
                     },
                     open: function(event, ui) { 
                        $(this).next(".help_text").hide();
                        $("#map_results").addClass("active");
                     },
                     close: function(event, ui) { 
                        $("#map_results").removeClass("active");
                        $(this).next(".help_text").show();
                     },
                    })
            .focusout(function(){ 
                    if ($("#id_latitude").val()=='' && $("#id_longitude").val()=='') {
                        hideMap();
                        $(this).val('');
                    }
                });
        
      $(".no_location").click(function() { 
              setLocationFields(null); 
              hideMap();  
              $(".gmaps_location").val('');
              $("#no_map_results").hide();
              $(".no_location").hide();
          });
 });