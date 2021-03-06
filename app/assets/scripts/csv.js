function downloadCSV(isAdmin) {
    // Init CSV array.
    var csv = [
        'data:text/csv;charset=utf-8,OBSERVED/EXPERIENCED,DATE,ADDRESS,CAR,'+
        'BUS,TRUCK,BICYCLE,PEDESTRIAN,CATEGORY,DESCRIPTION,INJURIES,INJURIES DESCRIPTION,'+
        'WEATHER/ROAD CONDITIONS'
    ];
    if (isAdmin) {
        csv[0] = csv[0]+',NUMBER OF DEATHS,PICTURE URL,,CONTACT NAME,CONTACT PHONE,CONTACT EMAIL';
    }
    markersDisplayedOnMap.forEach(function(marker) {
        var line = [
            marker.witness,
            marker.incidentDate,
            marker.locationName,
            marker.car,
            marker.bus,
            marker.truck,
            marker.bicycle,
            marker.pedestrian,
            marker.category,
            marker.description,
            marker.injuries,
            marker.injuries_description,
            marker.road_conditions
        ];
        if (isAdmin) {
            line.push(marker.deaths);
            line.push(marker.pictureUrl);
            line.push(marker.contactName);
            line.push(marker.contactPhone);
            line.push(marker.contactEmail);
        }

        csv.push(line.join(','));
    });
    var csvString = csv.join('\n');

    var encodedUri = encodeURI(csvString);
    var link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "my_data.csv");
    document.body.appendChild(link); // Required for FF

    // Download the data file.
    link.click();
}
