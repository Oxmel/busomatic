% for departure in schedules:
  <tr>
    <td id="line-name">{{departure['line_name']}}</td>
    <td id="line-direction">{{departure['line_direction']}}</td>
    <td id="line-schedule">{{departure['departure_time']}}</td>
  </tr>
% end
