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

    <div class="container">

      <div id="site-title" class="banner center-items hide-on-result">
        <span>Bus 'O' Matic</span>
      </div>

      <!-- Select menu -->
      <div id="menu" class="center-items hide-on-result">
        <select id="select-line">
          <option>Ligne</option>
          % for id, name in lines:
          <option value="{{id}}">{{name}}</option>
          % end
        </select>
        <select id="select-route">
          <option>Direction</option>
        </select>
        <select id="select-stop">
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
      <div id="result-table" class="show-on-result">
        <div class="banner info-block center-items">
          <img src="/static/images/bus_stop.png" /><span id="stop-name"></span>
        </div>
        <table id="print-stop">
        </table>
      </div>

      <!-- Reset button, send back to start page -->
      <div id="button" class="show-on-result">
        <button id="refresher" onclick="location.href='/'">Nouvelle Recherche</button>
      </div>

    <!-- Global container -->
    </div>

  </body>

</html>
