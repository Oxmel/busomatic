% for departure in schedules:
  <div class="departure">
    <div class="route-name">{{departure['line_name']}}</div>
    <div class="route-direction">{{departure['line_direction']}}</div>
    <div class="route-schedule">
      <div class="departure-time">{{departure['departure_time']}}</div>
      <div class="departure-delay">{{departure['departure_delay']}}</div>
    </div>
  </div>
% end
