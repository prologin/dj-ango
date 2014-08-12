function str2sec(s)
{
  var m = s.split(":");
  s = parseInt(m[1]);
  m = parseInt(m[0]);
  return 60 * m + s;
}

function sec2str(s)
{
  var m = Math.floor(s / 60);
  s = s % 60;
  return m + ":" + (s < 10 ? "0" : "") + s;
}

function update_time()
{
  var time = $("#timer").text();
  time = time.split("/");
  var total = time[1];
  time = time[0];
  time = str2sec(time) + 1;
  var max_sec = str2sec(total);
  if (time > max_sec)
  {
    location.reload();
    return;
  }
  time = sec2str(time);
  $("#timer").text(time + "/" + total);
  setTimeout(update_time, 1000);
}

$(document).ready(function()
{
  if ($("#timer").length != 0)
  {
    setTimeout(update_time, 1000);
  }
});
