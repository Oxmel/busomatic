// Name : selectedline.js
// Gathering schedule for selected line
// Also contains simple scripts for auto scroll and refresh


// Deux façons de masquer un élement :
// Avec .hide() et .show()
// ressource : http://api.jquery.com/hide/
// Ou avec .css('display', 'none')
// La deuxième méthode masque vraiment l'element et evite espaces blancs

    // Auto scroll function on "suite" anchor
    // Auto activate after stop choice
    function scroll() {
    var url=location.href;
    location.href="#suite";
    }

    // Action on button "Nouvelle recherche"
    // Clean url and send back to start page
    function refresh(){
    var sURL = unescape(window.location.pathname);
    window.location.replace(sURL);
    }

function init() {

    // Direction request for selected line, send result to selectDir function
    $("#selectLine").change(function() {
        var selectedLine = $("#selectLine").val();
        var url ="/direction/";
        var directions = url + selectedLine;
        $.get(directions, function(dirList) {
            $("#selectDir").html(dirList);
        });
    });

    // Stop request for selected direction, send result to selecstop function
    $("#selectDir").change(function() {
        var selectedDir = $("#selectDir").val();
        var url ="/arret/";
        var arrets = url + selectedDir;
        $.get(arrets, function(stopList) {
            $("#selectStop").html(stopList);
        });
    });

    // Schedule request for selected stop, send result to "printStop" table
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
            $("#banniere").css("display", "none");
            $("#menu").css("display", "none");
            // Show table and refresh button
            $("#tableau").css("display", "table-cell");
            $("#bouton").css("display", "table-row");
            // Scroll down once results are displayed
            scroll();
        });
        };
        curStop();
        setInterval(curStop, 30000);
    });

}

// Initializing script on page load
window.onload = init;
