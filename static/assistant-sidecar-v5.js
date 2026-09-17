(() => {
  const shell = document.getElementById("ai-chat-shell");
  const panel = document.getElementById("ai-panel");
  const toggle = document.getElementById("ai-toggle");
  const close = document.getElementById("ai-close");
  if (!shell || !panel || !toggle || !close || shell.dataset.sidecarReady === "true") return;
  shell.dataset.sidecarReady = "true";
  const openAssistant = () => { shell.hidden = false; panel.hidden = false; };
  const closeAssistant = () => { panel.hidden = true; shell.hidden = true; };
  toggle.addEventListener("click", openAssistant);
  close.addEventListener("click", closeAssistant);
  document.addEventListener("keydown", (event) => { if (event.key === "Escape" && !shell.hidden) closeAssistant(); });
})();
