function closeTutorial(tutorial) {
  if (tutorial) {
    tutorial.addEventListener("click", () => {
      document.getElementById("tutorial").style.display = "none";
      game.style.opacity = 1;
      game.style.filter = "blur(0px)";
    });
  }
}
