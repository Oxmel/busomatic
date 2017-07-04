// Name : datetime.js
// Get time and date
// Refresh both at regular interval

// Get current time (24h format)
var curTime=function() {
	var url ="/time";
	$.ajax({
		type:"GET",
		url,
		success: function(result){
		$("#heure").html(result);
		}
	});
};

// Auto refresh time every min 
$(document).ready(function() {
	setInterval(curTime, 60000);
	});

// Get date (dd/mm)
var curDate=function() {
	var url ="/date";
	$.ajax({
		type:"GET",
		url,
		success: function(result){
		$("#date").html(result);
		}
	});
};

// Auto refresh date every 2min
// TODO: Find a better method 
$(document).ready(function() {
	setInterval(curDate, 120000);
	});
