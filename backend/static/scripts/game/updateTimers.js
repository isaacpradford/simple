function updateTimerAnimation() {
  const now = Date.now();
  const elapsed = now - lastScoreUpdate;
  const progress = (elapsed % updateInterval) / updateInterval;
  const width = progress * 100;

  document.getElementById("timer-bar").style.width = `${width}%`;
}

function updateTimer() {
  let timerElement = document.getElementById("game-timer-hidden");
  let timer = parseInt(timerElement.textContent);
  timer += 1;
  timerElement.textContent = timer;
  document.getElementById("game-timer").textContent = formatTimer(timer);
}
