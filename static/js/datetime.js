// Name : datetime.js
// Get time and date
// Refresh both at regular interval

// Get current time (24h format)
var cur_time=function() {
	var url ="/time";
	$.ajax({
		type:"GET",
		url: url,
		success: function(result){
		$("#heure").html(result);
		}
	});
};

// Auto refresh time every min 
$(document).ready(function() {
	setInterval(cur_time, 60000);
	});

// Get date (dd/mm)
var cur_date=function() {
	var url ="/date";
	$.ajax({
		type:"GET",
		url: url,
		success: function(result){
		$("#date").html(result);
		}
	});
};

// Auto refresh date every 2min
// TODO: Find a better method 
$(document).ready(function() {
	setInterval(cur_date, 120000);
	});
