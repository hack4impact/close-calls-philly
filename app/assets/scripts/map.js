// Global Marker Wrappers and Map
var globalMarkers = null;
var globalMap = null;
var markerCluster = null;


// Geographic bounds centered according to incident report locations
var geographicBounds = null;

// Initial map center coordinates
INITIAL_CENTER_LAT = 39.952;
INITIAL_CENTER_LONG = -75.195;
initial_coords = new google.maps.LatLng(INITIAL_CENTER_LAT, INITIAL_CENTER_LONG);

// Bounds for the Date Slider. End date is current date.
var BOUNDS_MIN;
var BOUNDS_MAX = new Date();

// Take a list of markers and a map, put them on the map, set the
// minimum date, and set the location bounds
function storeMarkerState(markers, map, minDate, bounds, oms) {
    globalMarkers = markers;
    globalMap = map;
    markerCluster = new MarkerClusterer(map, markers, {gridSize: 50, maxZoom: 15, minimumClusterSize: 15, imagePath: 'static/images/clusterer/m'});
    for (mw = 0; mw < globalMarkers.length; mw++)
    {
        (globalMarkers[mw]).setMap(globalMap);
        oms.addMarker(globalMarkers[mw]);

    }
    BOUNDS_MIN = minDate;
    geographicBounds = bounds;
    map.fitBounds(bounds);
}

// Use Google geocoder to update geolocation given an address through
// the address search box
function update_center() {
    geocoder = new google.maps.Geocoder();
    address = $("#address").val();
    if (geocoder) {
        geocoder.geocode( { 'address': address},
        function(results, status) {
            if (status == google.maps.GeocoderStatus.ZERO_RESULTS) {
                $('#address_error').modal('show');
            }
            else if (status != google.maps.GeocoderStatus.OK) {
                $('#geocode_error').modal('show');
            }
            else {
                globalMap.setCenter(results[0].geometry.location);
            }
            /*$('.close.icon').on('click', function() {
                $(this).parent().hide();
            });*/
        });
    }
}

// Heavily inspired by https://jsfiddle.net/mi3afzal/ogsvzacz/2/
// Adds a "geolocate" button to the map.
function addLocationButton(map) {
	var controlDiv = document.createElement('div');

	var firstChild = document.createElement('button');
	firstChild.style.backgroundColor = '#fff';
	firstChild.style.border = 'none';
	firstChild.style.outline = 'none';
	firstChild.style.width = '28px';
	firstChild.style.height = '28px';
	firstChild.style.borderRadius = '2px';
	firstChild.style.boxShadow = '0 1px 4px rgba(0,0,0,0.3)';
	firstChild.style.cursor = 'pointer';
	firstChild.style.marginRight = '10px';
	firstChild.style.padding = '0px';
	firstChild.title = 'Your Location';
	controlDiv.appendChild(firstChild);

	var secondChild = document.createElement('div');
	secondChild.style.margin = '5px';
	secondChild.style.width = '18px';
	secondChild.style.height = '18px';
	secondChild.style.backgroundImage = 'url(https://maps.gstatic.com/tactile/mylocation/mylocation-sprite-1x.png)';
	secondChild.style.backgroundSize = '180px 18px';
	secondChild.style.backgroundPosition = '0px 0px';
	secondChild.style.backgroundRepeat = 'no-repeat';
	secondChild.id = 'you_location_img';
	firstChild.appendChild(secondChild);

	google.maps.event.addListener(map, 'dragend', function() {
		$('#you_location_img').css('background-position', '0px 0px');
	});

	firstChild.addEventListener('click', function() {
		var imgX = '0';
		var animationInterval = setInterval(function(){
			if(imgX == '-18') imgX = '0';
			else imgX = '-18';
			$('#you_location_img').css('background-position', imgX+'px 0px');
		}, 500);
		if(navigator.geolocation) {
			navigator.geolocation.getCurrentPosition(function(position) {
				var latlng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
				map.setCenter(latlng);
				clearInterval(animationInterval);
				$('#you_location_img').css('background-position', '-144px 0px');
			});
		}
		else{
			clearInterval(animationInterval);
			$('#you_location_img').css('background-position', '0px 0px');
		}
	});

	controlDiv.index = 1;
	map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(controlDiv);
}

function addCenterButton(map) {
    var centerDiv = document.createElement('div');

    var centerButton = document.createElement('button');
    centerButton.style.backgroundColor = '#fff';
    centerButton.style.border = 'none';
    centerButton.style.outline = 'none';
    centerButton.style.width = '28px';
    centerButton.style.height = '28px';
    centerButton.style.borderRadius = '2px';
    centerButton.style.boxShadow = '0 1px 4px rgba(0,0,0,0.3)';
    centerButton.style.cursor = 'pointer';
    centerButton.style.marginBottom = '10px';
    centerButton.style.marginRight = '10px';
    centerButton.style.padding = '0px';
    centerButton.style.textAlign = 'center';
    centerButton.innerHTML = '  <i class="reply icon"></i>';
    centerButton.value = 'Reports Center';
    centerButton.title = 'Reports Center';
    centerButton.id = 'centerButton';
    centerDiv.appendChild(centerButton);

    centerButton.addEventListener('click', function() {
        map.fitBounds(geographicBounds);
    });
    centerDiv.index = 1;
    map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(centerDiv);
}

// Get address submit event
$(document).ready(function() {
    $('#addressForm').on('submit', function (event) {
        update_center();
        return false;
    });
});

function filterMarkers(bounds) {
    var markersDisplayedOnMap = [];
    for (mw = 0; mw < globalMarkers.length; mw++) {
        if (bounds === null || bounds.contains(globalMarkers[mw].getPosition())) {
            globalMarkers[mw].setMap(globalMap);
            markersDisplayedOnMap.push(globalMarkers[mw]);
        } else {
            globalMarkers[mw].setMap(null);
        }
    }
    markerCluster.clearMarkers();
    markerCluster.addMarkers(markersDisplayedOnMap);
}
