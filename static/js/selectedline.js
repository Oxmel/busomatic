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
    // Send result to the select element 'select-route'
    $("#select-line").change(function() {
        var selectedLine = $("#select-line").val();
        var url ="/direction/";
        var directions = url + selectedLine;
        $.get(directions, function(dirList) {
            $("#select-route").html(dirList);
        });
    });

    // Grab available stops after the user has selected a direction
    // Send result to the select element 'select-stop'
    $("#select-route").change(function() {
        var selectedDir = $("#select-route").val();
        var url ="/arret/";
        var arrets = url + selectedDir;
        $.get(arrets, function(stopList) {
            $("#select-stop").html(stopList);
        });
    });

    // Request schedule for selected stop, send result to 'print-stop' table
    $("#select-stop").change(function() {
        var curStop=function(){
            var stopName = $("#select-stop option:selected").text();
            var selectedStop = $("#select-stop").val();
            var url ="/horaire/";
            var horaires = url + selectedStop;
            $.get(horaires, function(schedule) {
                // Sending results to the table element
                $("#print-stop").html(schedule);
                $("#stop-name").html(stopName);
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
