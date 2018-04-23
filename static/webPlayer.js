var audioPlayer = function() {
  var currentTrackIndex = null;
  var documentAudio = document.getElementById("audio");
  var documentMainButton = document.querySelector(".large-toggle-btn");
  var documentNextButton = document.querySelector(".next-track-btn");
  var documentPreviousButton = document.querySelector(".previous-track-btn");
  var documentSmallToggle = document.getElementsByClassName("small-toggle-btn");
  var documentProgressBar = document.querySelector(".progress-box");
  var documentPlayListRows = document.getElementsByClassName("play-list-row");
  var documentTrackInfoBox = document.querySelector(".track-info-box");

  var playAhead = false;
  var progressCounter = 0;
  var progressBarIndicator  = documentProgressBar.children[0].children[0].children[1];
  var trackLoaded = false;

  var _getY = function(e) {
    var yCoord = null;
    if (e.layerX || e.layerX == 0) { 
      yCoord = e.layerY;
    }
    return yCoord;
  };

  var _getX = function(e) {
    var xCoord = null;
    if (e.layerX || e.layerX == 0) { 
      xCoord = e.layerX;
    }
    return xCoord;
  };

  var _handleProgressIndicatorClick = function(e) {
    var progressBar = document.querySelector(".progress-box");
    var xCoord = _getX(e).x;
    if (xCoord <= 0){
      xCoord = 0;
    }
    return (xCoord - progressBar.offsetLeft) / progressBar.children[0].offsetWidth;
  };

  var initPlayer = function() {

    if (currentTrackIndex == null){
      documentPreviousButton.disabled = true;
    }
    if (currentTrackIndex == documentPlayListRows.length){
      documentNextButtonButton.disabled = true;
    }

    for (var i = 0; i < documentPlayListRows.length; i++) {
      var smallToggleBtn = documentSmallToggle[i];
      var playListLink = documentPlayListRows[i].children[2].children[0];

      playListLink.addEventListener("click", function(e) {
        var selectedTrack = this.parentNode.parentNode.getAttribute("data-track-row");
        if (selectedTrack != currentTrackIndex) {
          _resetPlayStatus();
          currentTrackIndex = null;
          trackLoaded = false;
        }

        if (trackLoaded == false) {
          currentTrackIndex = selectedTrack;
          _setTrack();
        } else {
          _playBack(this);
        }
      }, false);

      smallToggleBtn.addEventListener("click", function(e) {
        var selectedTrack = this.parentNode.getAttribute("data-track-row");
        if (selectedTrack != currentTrackIndex) {
          _resetPlayStatus();
          currentTrackIndex = null;
          trackLoaded = false;
        }

        if (trackLoaded == false) {
          currentTrackIndex = selectedTrack;
          _setTrack();
        } else {
          _playBack(this);
        }
      }, false);
    }

    documentAudio.addEventListener("timeupdate", _trackTimeChanged, false);
    documentAudio.addEventListener("ended", function(e) {
      _trackHasEnded();
    }, false);

    documentMainButton.addEventListener("click", function(e) {
      if (trackLoaded == false) {
        currentTrackIndex = 1;
        _setTrack()
      } else {
        _playBack();
      }
    }, false);

    documentNextButton.addEventListener("click", function(e) {
      if (this.disabled != true) {
        currentTrackIndex++;
        trackLoaded = false;
        _resetPlayStatus();
        _setTrack();
      }
    }, false);

    documentPreviousButton.addEventListener("click", function(e) {
      if (this.disabled != true) {
        currentTrackIndex--;
        trackLoaded = false;
        _resetPlayStatus();
        _setTrack();
      }
    }, false);

    progressBarIndicator .addEventListener("mousedown", _mouseDown, false);
    window.addEventListener("mouseup", _mouseUp, false);
  };

  var _mouseDown = function(e) {
    window.addEventListener("mousemove", _moveProgressIndicator, true);
    audio.removeEventListener("timeupdate", _trackTimeChanged, false);
    playAhead = true;
  };

  var _mouseUp = function(e) {
    if (playAhead == true) {
      var duration = parseFloat(audio.duration);
      var progressIndicatorClick = parseFloat(_handleProgressIndicatorClick(e));
      window.removeEventListener("mousemove", _moveProgressIndicator, true);
      audio.currentTime = duration * progressIndicatorClick;
      audio.addEventListener("timeupdate", _trackTimeChanged, false);
      playAhead = false;
    }
  };

  var _moveProgressIndicator = function(e) {
    var progressBarIndicator = documentProgressBar.children[0].children[0].children[1];
    var progressBarIndicatorWidth = progressBarIndicator.offsetWidth;
    var progressBarWidth = documentProgressBar.children[0].offsetWidth - progressBarIndicatorWidth;
    var newPosition = _getX(e).x - documentProgressBar.offsetLeft;

    if ((newPosition >= 1) && (newPosition <= progressBarWidth)) {
      progressBarIndicator.style.left = newPosition + ".px";
    }
    if (newPosition < 0) {
      progressBarIndicator.style.left = "0";
    }
    if (newPosition > progressBarWidth) {
      progressBarIndicator.style.left = progressBarWidth + "px";
    }
    else{
      progressBarIndicator.style.left = "0";
    }
  };

  var _playBack = function() {
    if (documentAudio.paused) {
      documentAudio.play();
      _updatePlayStatus(true);
    } else {
      documentAudio.pause();
      _updatePlayStatus(false);
    }
  };

  var _setTrack = function() {
    var songURL = documentAudio.children[currentTrackIndex - 1].src;

    documentAudio.setAttribute("src", songURL);
    documentAudio.load();

    trackLoaded = true;

    var trackTitleBox = document.querySelector(".player .info-box .track-info-box .track-title-text");
    var trackTitle = documentPlayListRows[currentTrackIndex - 1].children[2].outerText;
    trackTitleBox.innerHTML = "";
    trackTitleBox.innerHTML = trackTitle;
    document.title = trackTitle;

    for (var i = 0; i < documentPlayListRows.length; i++) {
      documentPlayListRows[i].children[2].className = "track-title";
    }
    documentPlayListRows[currentTrackIndex - 1].children[2].className = "track-title active-track";
    documentTrackInfoBox.style.visibility = "visible";
    _playBack();
  };

  var _trackHasEnded = function() {
    if (currentTrackIndex == documentPlayListRows.length){
      currentTrackIndex = 1;
    }
    else{
      currentTrackIndex = currentTrackIndex + 1;
    }
    trackLoaded = false;
    _resetPlayStatus();
    _setTrack();
  };

  var _trackTimeChanged = function() {
    var currentTimeBox = document.querySelector(".player .info-box .track-info-box .audio-time .current-time");
    var currentTime = audio.currentTime;
    var duration = audio.duration;
    var durationBox = document.querySelector(".player .info-box .track-info-box .audio-time .duration");
    var trackCurrentTime = _timePassed(currentTime);
    var trackDuration = '00:30'

    currentTimeBox.innerHTML = null;
    currentTimeBox.innerHTML = trackCurrentTime;
    durationBox.innerHTML = null;
    durationBox.innerHTML = trackDuration;

    _updateProgressIndicator(audio);
  };

  var _timePassed = function(seconds) {
    var sec = Math.round(seconds);
    var time = 0;
    sec = Math.round(sec % 60);
    var min = '00' 
    if (sec >= 10){
      sec;
    }
    else{
      sec = '0' + sec;
    }

    time = min + ':' + sec;
    return time;
  };

  var _updatePlayStatus = function(audioPlaying) {
    if (audioPlaying) {
      documentMainButton.children[0].className = "large-pause-btn";
      documentSmallToggle[currentTrackIndex - 1].children[0].className = "small-pause-btn";
    } else {
      documentMainButton.children[0].className = "large-play-btn";
      documentSmallToggle[currentTrackIndex - 1].children[0].className = "small-play-btn";
    }

    if (currentTrackIndex == 1) {
      documentPreviousButton.disabled = true;
      documentPreviousButton.className = "previous-track-btn disabled";
    } else if (currentTrackIndex > 1 && currentTrackIndex != documentPlayListRows.length) {
      documentPreviousButton.disabled = false;
      documentPreviousButton.className = "previous-track-btn";
      documentNextButton.disabled = false;
      documentNextButton.className = "next-track-btn";
    } else if (currentTrackIndex == documentPlayListRows.length) {
      documentNextButton.disabled = true;
      documentNextButton.className = "next-track-btn disabled";
    }
  };

  var _updateProgressIndicator = function() {
    var currentTime = documentAudio.currentTime;
    var duration = documentAudio.duration;
    var indicatorLocation = 0;
    var progressBarWidth = documentProgressBar.offsetWidth;
    var progressIndicatorWidth = progressBarIndicator .offsetWidth;
    var progressBarIndicatorWidth = progressBarWidth - progressIndicatorWidth;

    indicatorLocation = progressBarIndicatorWidth * (currentTime / duration);
    progressBarIndicator.style.left = indicatorLocation + "px";
  };

  var _resetPlayStatus = function() {
    documentMainButton.children[0].className = "large-play-btn";
    for (var i = 0; i < documentSmallToggle.length; i++) {
      if (documentSmallToggle[i].children[0].className == "small-pause-btn") {
        documentSmallToggle[i].children[0].className = "small-play-btn";
      }
    }
  };
  return {initPlayer: initPlayer};
};

(function() {
  var player = new audioPlayer();

  player.initPlayer();
})();