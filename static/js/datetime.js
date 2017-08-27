// Name : datetime.js

// Get time (24h format)
var curTime=function() {
	var now = new Date();
	var hours = now.getHours();
	var minutes = now.getMinutes();
	if (hours < 10) {hours = "0" + hours;}
	if (minutes < 10) {minutes = "0" + minutes;}
	var time = hours + 'h' + minutes;
	$("#heure").html(time);

};

// Get date (dayname/daynum/month format)
// Translate current month and current dayname to fr
var curDate=function() {
	dicMonth = new Array("Janv.", "Fev.", "Mars", "Avr.", "Mai", "Juin",
						"Juil.", "Août", "Sept.", "Oct.", "Nov.", "Déc.");
	dicDay = new Array("Dim.", "Lun.", "Mar.", "Mer.", "Jeu.", "Ven.", "Sam.");
	var now = new Date();
	var dayNum = now.getUTCDate();
	var day = now.getDay();
	dayTest = dicDay[day];
	var month = now.getUTCMonth();
	var testMonth = dicMonth[month];
	//if (day < 10) {day = "0" + day;}
	$("#date").html(dayTest + ' ' + dayNum + ' ' + testMonth);
};


// Display time and date when page is loaded
// Auto refresh time every 60 seconds
$(document).ready(function() {
	curTime();
	curDate();
	setInterval(curTime, 60000);
	});
