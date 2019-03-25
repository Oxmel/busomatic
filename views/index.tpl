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
<div class="container">

    <!-- Banner -->
    <div id="banniere" class="banner site-title center-items">
        <span>Bus 'O' Matic</span>
    </div>

    <!-- Select line menu -->
    <div id="menu" class="menu center-items">
        <select id="selectLine">
            <option>Ligne</option>
            % for id, name in lines:
            <option value="{{id}}">{{name}}</option>
            % end
        </select>
        <select id="selectDir">
            <option>Direction</option>
        </select>
        <select id="selectStop">
            <option>Arrêt</option>
        </select>
    </div>


    <div class="banner info-block border-bottom center-items">
            <img src="/static/images/calendar.png" /><span id="date"></span>
            <img src="/static/images/clock.png" /><span id="heure"></span>
    </div>

    <div class="banner info-block center-items">
            <img src="/static/images/weather.png" /><span>{{weather}}</span>
            <img src="/static/images/thermometer.png" /><span>{{temp}}°C</span>
            <img src="/static/images/wind.png" /><span>{{wind}}km/h</span>
    </div>


    <!-- Results table -->
    <div id="tableau">

        <div class="banner info-block center-items">
            <img src="/static/images/bus_stop.png" /><span id="stopName"></span>
        </div>

        <table id="printStop">
        </table>

    </div>

    <!-- Reset button, send back to start page -->
    <div id="bouton">
        <button id="refresher" onclick="location.href='/'">Nouvelle Recherche</button>
    </div>

<!-- div of "page" -->
</div>

</body>
</html>
