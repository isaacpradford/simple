function playMessageAnimation(success, button, message) {
    const rect = button.getBoundingClientRect();
    const msg = document.createElement("div");
    msg.classList.add("response-message");
    msg.textContent = message;

    // Position relative to the button
    msg.style.left = `${rect.left + rect.width / 2}px`;
    msg.style.top = `${rect.top - 10}px`;
    msg.style.position = "fixed";

    msg.style.color = success ? "#46d467" : "#ff5656";

    const angle = 45 + Math.random() * 90; // Random angle from 45-135
    const distance = -100; // Pixels
    const angleRad = (angle * Math.PI) / 180;
    const dx = Math.cos(angleRad) * distance;
    const dy = Math.sin(angleRad) * distance;

    const rotation = Math.random() * 60 - 30;

    msg.style.setProperty("--dx", `${dx}px`);
    msg.style.setProperty("--dy", `${dy}px`);
    msg.style.setProperty("--rotation", `${rotation}deg`);

    document.body.appendChild(msg);

    setTimeout(() => {
      msg.remove();
    }, 2000);
  }