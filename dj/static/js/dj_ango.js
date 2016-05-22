const DELAY_ELAPSED_TIMER = 500;
const DELAY_NOW_PLAYING = 2000;
const DELAY_PLAYING_NEXT = 5000;
const DELAY_VOLUME = 5000;

$(function () {
  let page_loaded_at = new Date();
  let elapsedTimeout;

  let $timer = $("#timer");
  let $timerBar = $("#timer-bar");
  let $stubPlayingNext = $("#stub-playing-next");
  let $stubNowPlaying = $("#stub-now-playing");
  let $volume = $('#volume');

  function sec2str(s) {
    s = parseInt(s);
    return Math.floor(s / 60) + ":" + ('00' + (s % 60)).slice(-2);
  }

  function updateElapsed() {
    let elapsed = parseInt($timer.attr('data-elapsed')) + ((new Date() - page_loaded_at) / 1000);
    let duration = parseInt($timer.attr('data-duration'));
    elapsed = Math.min(elapsed, duration);
    let ratio = elapsed / duration * 100;
    $timerBar.attr("aria-valuenow", ratio).attr("style", "width: " + ratio + "%");
    $timer.text(sec2str(elapsed));
    elapsedTimeout = setTimeout(updateElapsed, DELAY_ELAPSED_TIMER);
  }

  function updatePlayingNext() {
    $.get('/stub/playing-next')
      .then((content) => {
        $stubPlayingNext.find('table').fadeOut('fast', () => {
          $stubPlayingNext.html(content);
          $stubPlayingNext.find('table').hide().fadeIn('fast');
        })
      });
    setTimeout(updatePlayingNext, DELAY_PLAYING_NEXT);
  }

  function updateNowPlaying() {
    $.get('/stub/now-playing')
      .then((content) => {
        clearTimeout(elapsedTimeout);
        page_loaded_at = new Date();
        $stubNowPlaying.html(content);
        $timer = $("#timer");
        $timerBar = $("#timer-bar");
        updateElapsed();
      });
    setTimeout(updateNowPlaying, DELAY_NOW_PLAYING);
  }

  function updateVolume() {
    $.get('/volume').then((volume) => $volume.val(volume));
  }

  if ($timer.length) {
    updateElapsed();
    setTimeout(updatePlayingNext, DELAY_PLAYING_NEXT);
    setTimeout(updateNowPlaying, DELAY_NOW_PLAYING);
  }
  if ($volume.length) {
    $volume.change(() => {
      $.post('/volume', '' + $volume.val());
    });
    setInterval(updateVolume, DELAY_VOLUME);
  }

  $('button[name=copy-to-fields]').click(function(e) {
    e.preventDefault();
    let $tr = $(this).closest('tr');
    $('input[name=artist]').val($tr.attr('data-artist'));
    $('input[name=title]').val($tr.attr('data-title'));
  });

});
