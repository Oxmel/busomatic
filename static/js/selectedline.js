/*
Name : selectedline.js
Gathers schedule for selected line
Also contains simple scripts for auto scroll and refresh

We use the same single page for the index and for displaying results
so we want to to hide certain elements when a search is performed.
This is achieved by using (#'item_name').css('display', 'none')
Other methods using jquery can be found at 'api.jquery.com/hide'
*/


function init() {

    // Grab available directions after the user has selected a line
    // Send result to the select element 'selectDir'
    $("#selectLine").change(function() {
        var selectedLine = $("#selectLine").val();
        var url ="/direction/";
        var directions = url + selectedLine;
        $.get(directions, function(dirList) {
            $("#selectDir").html(dirList);
        });
    });

    // Grab available stops after the user has selected a direction
    // Send result to the select element 'selectStop'
    $("#selectDir").change(function() {
        var selectedDir = $("#selectDir").val();
        var url ="/arret/";
        var arrets = url + selectedDir;
        $.get(arrets, function(stopList) {
            $("#selectStop").html(stopList);
        });
    });

    // Request schedule for selected stop, send result to 'printStop' table
    $("#selectStop").change(function() {
        var curStop=function(){
            var stopName = $("#selectStop option:selected").text();
            var selectedStop = $("#selectStop").val();
            var url ="/horaire/";
            var horaires = url + selectedStop;
            $.get(horaires, function(schedule) {
                // Sending results to the table element
                $("#printStop").html(schedule);
                $("#stopName").html(stopName);
                // Hide menu and header, keep footer visible
                $(".hide-on-result").css("display", "none");
                // Show table and refresh button
                $(".show-on-result").css("display", "flex");
            });
        };
        curStop();
        setInterval(curStop, 30000);
    });

}

// Initializing script on page load
window.onload = init;
