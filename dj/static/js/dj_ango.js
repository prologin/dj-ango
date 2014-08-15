var timer_timeout;

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
    update_now_playing();
    return;
  }
  var ratio = 100 * time / max_sec;
  time = sec2str(time);
  $("#timer-bar").attr("aria-valuenow", ratio);
  $("#timer-bar").attr("style", "width: " + ratio + "%");
  $("#timer-remain").attr("style", "width: " + (100 - ratio) + "%");
  $("#timer").text(time + "/" + total);
  timer_timeout = setTimeout(update_time, 1000);
}

function vote_category(c)
{
  vote_page(1, c);
}

function vote_page(p, c)
{
  var requrl = "/vote/get_" + c + "/" + p;
  var url = "/vote/" + ((c == "all") ? "" : (c + "/")) + p;
  var span = $("#page");
  $(".active").removeClass("active");
  $("#" + c).addClass("active");
  span.fadeOut();
  $.get(requrl, {}, function(data)
  {
    span.html(data);
  });
  span.fadeIn();
  history.pushState({}, "", url);
}

function update_now_playing()
{
  var span = $("#now-playing");
  span.fadeOut(1000);
  $.get('/now_playing/', {}, function(data)
  {
    span.html(data);
  });
  span.fadeIn(1000);
  clearTimeout(timer_timeout);
  timer_timeout = setTimeout(update_time, 1000);
}

$(document).ready(function()
{
  if ($("#timer").length != 0)
  {
    timer_timeout = setTimeout(update_time, 1000);
  }
});
