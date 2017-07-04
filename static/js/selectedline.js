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
	window.location.replace( sURL );
	}

 function init() {


	// Direction request for selected line, send result to selectdir function
	$("#selectline").change(function() {
		var linetarget = document.getElementById("selectline");
		var selectedline = linetarget.options[linetarget.selectedIndex].value;
		var url ="/direction/";
		var directions = url+selectedline;
		$.ajax({
		type:"GET",
            url: directions,
            success: function(retour){
            $("#selectdir").html(retour);
            }
         });
		return false;
	});

	// Stop request for selected direction, send result to selecstop function
	$("#selectdir").change(function() {
		var dirtarget = document.getElementById("selectdir");
		var selecteddir = dirtarget.options[dirtarget.selectedIndex].value;
		var url ="/arret/";
		var arrets = url+selecteddir;
		 $.ajax({
		type:"GET",
            url: arrets,
            success: function(retour){
            $("#selectstop").html(retour);
            }
         });
		return false;

	});

	// Schedule request for selected stop, send result to "printstop" table
	$("#selectstop").change(function() {
		var curStop=function(){
		var stoptarget = document.getElementById("selectstop");
		var stop_name = stoptarget.options[stoptarget.selectedIndex].text;
		var selectedstop = stoptarget.options[stoptarget.selectedIndex].value;
		var url ="/horaire/";
		var horaires = url+selectedstop;
		 $.ajax({
		type:"GET",
            url: horaires,
            success: function(retour){
			// Sending results to the table element
            $("#printstop").html(retour);
			$("#stop_name").html(stop_name);
			// Hide menu and header, keep footer visible
			$("#banniere").css("display", "none");
			$("#menu").css("display", "none");
			// Show table and refresh button
			$("#tableau").css("display", "table-cell");
			$("#bouton").css("display", "table-row");
			// Scroll down once results are displayed
			scroll();
            }
         });
		return false;
	};
		curStop();
		setInterval(curStop, 30000);
	});

}

// Initializing script on page load
window.onload = init;


