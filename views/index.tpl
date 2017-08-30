<!DOCTYPE html>

<html>
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1 user-scalable=0">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="default">
        <link href="/static/images/bus-icon-mobile.png" rel="apple-touch-icon" />
        <link href="/static/images/bus-icon-mobile.png" rel="icon" />
        <link rel="stylesheet"type="text/css"href="/static/style/style.css"/>
        <link rel="icon" type="image/png" href="/static/images/favicon.png"/>   
        <script src="https://code.jquery.com/jquery-1.12.4.min.js"></script>
        <script src="/static/js/datetime.js"></script>
        <script src="/static/js/selectedline.js"></script>
        <title>Bus'O'Matic</title>
    </head>

<body>
    <!-- Hide url bar on mobile devices to show in full screen -->
    <!-- <script>window.scrollTo(0,1)</script --> 

<!-- Global container -->
<div id="page">

    <!-- Banner -->
    <div id="banniere">
        <span id="titre">Bus 'O' Matic</span>
    </div>

    <!-- Select line menu -->
    <div id="menu">
        <select id="selectline">
            <option>Ligne</option>  
        % for id, name in lines:
            <option value="{{id}}">
            {{name}}
            </option>
        %end
        </select>
        <select id="selectdir">
            <option>Direction</option>
        </select>
        <select id="selectstop">
            <option>Arrêt</option>
        </select>
    </div>

    <!-- Floating  menu -->
    <div id="footer">
        <a name="suite"></a>
        <p id="date_heure">
            <img id="img_date" src="/static/images/calendar.png">
            <span id="date"></span>
            <img id="img_heure" src="/static/images/clock.png">
            <span id="heure"></span>
        </p>
        <p id="meteo">
            <img src="/static/images/weather.png">
            <span id="temps">{{forecast}}</span>
            <img src="/static/images/thermometer.png">
            <span id="temperature">{{temp}}°C</span> 
            <img src="/static/images/wind.png">
            <span id="vent">{{wind}}km/h</span>
        </p>
    </div>
    
    <!-- Results table -->
    <div id="tableau">
        <div id="table_header">
            <img id="stop_img" src="/static/images/bus_stop.png">
            <span id="stop_name"></span>
        </div>
        <table id="printstop" align="center">
        </table>
    </div>
    
    <!-- Reset button, send back to start page -->
    <div id="bouton">
        <button id="refresher" onclick="refresh()">Nouvelle Recherche</button>
    </div>

<!-- div of "page" -->
</div>

</body>
</html>
