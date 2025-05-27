function loadTooltipsAndTutorial() {
  document.addEventListener("DOMContentLoaded", () => {
    const shopButton = document.getElementById("shop-icon");
    const game = document.getElementById("simple-game");
    let shopOpen = false;

    if (shopButton && game) {
      shopButton.addEventListener("click", () => {
        const isMobile = window.innerWidth <= 768;

        if (isMobile) {
          if (shopOpen) {
            game.style.gridTemplateRows = "1fr 0fr";
          } else {
            game.style.gridTemplateRows = ".5fr .5fr";
          }
        } else {
          if (shopOpen) {
            game.style.gridTemplateColumns = "1fr 0fr";
          } else {
            game.style.gridTemplateColumns = "1fr 1fr";
          }
        }

        shopOpen = !shopOpen;
      });
    }

    const tutorialOpen = document.getElementById("tutorial");

    if (tutorialOpen) {
      game.style.opacity = 0.2;
      game.style.filter = "blur(2px)";
    }

    const tooltipEnabled = localStorage.getItem("tooltips") == "true";
    if (!tooltipEnabled) return;

    const tooltip = document.createElement("div");
    tooltip.className = "tooltip";
    document.body.appendChild(tooltip);

    document.querySelectorAll("[data-tooltip]").forEach((el) => {
      el.addEventListener("mouseenter", (e) => {
        const message = el.getAttribute("data-tooltip");
        tooltip.textContent = message;
        tooltip.classList.add("show");
      });

      el.addEventListener("mousemove", (e) => {
        tooltip.style.left = e.pageX + 10 + "px";
        tooltip.style.top = e.pageY + 10 + "px";
      });

      el.addEventListener("mouseleave", () => {
        tooltip.classList.remove("show");
      });
    });
  });
}
