// Name : datetime.js

// Get time (24h format)
var curTime=function() {
    var now = new Date();
    var hours = now.getHours();
    var minutes = now.getMinutes();
    if (hours < 10) {hours = "0" + hours;}
    if (minutes < 10) {minutes = "0" + minutes;}
    var time = hours + "h" + minutes;
    $("#heure").html(time);

};

// Get date (dayname/daynum/month format)
// Translate current month and current dayname to fr
var curDate=function() {
    var dicMonth = new Array("Janv.", "Fev.", "Mars", "Avr.", "Mai", "Juin",
                        "Juil.", "Août", "Sept.", "Oct.", "Nov.", "Déc.");
    var dicDay = new Array("Dim.", "Lun.", "Mar.", "Mer.", "Jeu.", "Ven.", "Sam.");
    var now = new Date();
    // Current day (numeric format)
    var dayNum = now.getUTCDate();
    // Current day of the week (0-6)
    var day = now.getDay();
    var dayFr = dicDay[day];
    // Current month (0-11)
    var month = now.getUTCMonth();
    var monthFr = dicMonth[month];
    //if (day < 10) {day = "0" + day;}
    $("#date").html(dayFr + " " + dayNum + " " + monthFr);
};


// Display time and date when page is loaded
// Auto refresh time every 60 seconds
$(document).ready(function() {
    curTime();
    curDate();
    setInterval(curTime, 60000);
    });
