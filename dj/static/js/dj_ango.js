var timer_timeout;
var timer_votes_reload;

function fade(obj, data, time)
{
  obj.fadeOut(time, function()
  {
    obj.html(data);
    obj.fadeIn(time);
  });
}

function fade_callback(obj, time)
{
  return function(data)
  {
    fade(obj, data, time);
  }
}

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
    update_next();
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
  $.get(requrl, {}, fade_callback(span, 300));
  history.pushState({}, "", url);
}

function add_vote(id, p, c)
{
  $.post("/vote/add/", {song_id: id}, function(data) { vote_page(p, c); });
}

function del_vote(id, p, c)
{
  $.post("/vote/rm/", {song_id: id}, function(data) { vote_page(p, c); });
}

function add_vote_idx(id)
{
  $.post("/vote/add/", {song_id: id}, function(data) { update_next(); });
}

function del_vote_idx(id)
{
  $.post("/vote/rm/", {song_id: id}, function(data) { update_next(); });
}

function add_search()
{
  var search = $("#search").val();
  $.get("/search/" + search, {}, function(data) { $("#results").html(data); });
  return false;
}

function add_pending(link, source)
{
  if ($("#title").val().length == 0)
  {
    alert("The title field is required");
    return;
  }
  var data =
  {
    title: $("#title").val(),
    artist: $("#artist").val(),
    link: link,
    source: source
  };
  $.post("/add_pending/", data, function(data)
  {
      update_pending();
      $("#result_list").slideUp(1000, function() {  $("#result_list").text(""); });
  });
}

function update_pending()
{
  var span = $("#pending");
  $.get('/add/pending/', {}, fade_callback(span, 1000));
}

function update_now_playing()
{
  var span = $("#now-playing");
  $.get('/now_playing/', {}, fade_callback(span, 1000));
  clearTimeout(timer_timeout);
  timer_timeout = setTimeout(update_time, 1000);
}

function validate(id)
{
  var data =
  {
    title: $("#title" + id).val(),
    artist: $("#artist" + id).val(),
    link: $("#link" + id).val()
  };
  $.post('/validate/' + id, data, function (d) { update_validate_pending(); });
}

function nuke(id)
{
  $.get('/nuke/' + id, {}, function (d) { update_validate_pending(); });
}

function update_validate_pending()
{
  var span = $("#pending");
  $.get('/pending/', {}, fade_callback(span, 1000));
}

function update_next()
{
  var span = $("#next");
  $.get('/next/', {}, function(data)
  {
    span.html(data);
  });
  clearTimeout(timer_votes_reload);
  timer_timeout = setTimeout(update_next, 5000);
}

$(document).ready(function()
{
  if ($("#timer").length != 0) // index
  {
    timer_timeout = setTimeout(update_time, 1000);
    timer_votes_reload = setTimeout(update_next, 5000);
  }
  
  if ($("#search").length != 0) // add
  {
    $("#search").keyup(function(event)
    {
      if(event.keyCode == 13) { $("#search_button").click(); }
    });
  }

  $.ajaxSetup({
    beforeSend: function(xhr, settings)
    {
      if (!this.crossDomain) { xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken")); }
    }
  });
});
