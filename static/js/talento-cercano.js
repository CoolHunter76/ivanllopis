(() => {
  "use strict";
  const clouds = document.querySelectorAll("[data-talent-cloud]");
  if (!matchMedia("(prefers-reduced-motion: reduce)").matches && matchMedia("(pointer: fine)").matches) {
    const started = performance.now();
    const floatClouds = (now) => {
      clouds.forEach((cloud, index) => {
        if (!cloud.matches(":hover,:focus-visible")) {
          const x = Math.sin((now - started) / 2900 + index) * 7;
          const y = Math.cos((now - started) / 3400 + index * 1.3) * 6;
          cloud.style.translate = `${x}px ${y}px`;
        }
      });
      requestAnimationFrame(floatClouds);
    };
    requestAnimationFrame(floatClouds);
  }
  const dialog = document.querySelector("[data-talent-dialog]");
  const video = document.querySelector("[data-talent-video]");
  const close = document.querySelector("[data-talent-close]");
  if (!dialog || !video || !close) return;
  const stop = () => { video.pause(); video.removeAttribute("src"); video.load(); };
  document.querySelectorAll("[data-video]").forEach((button) => {
    button.addEventListener("click", () => {
      video.src = button.dataset.video;
      dialog.showModal();
      video.play().catch(() => undefined);
    });
  });
  close.addEventListener("click", () => dialog.close());
  dialog.addEventListener("close", stop);
  dialog.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); });
})();
