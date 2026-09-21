(() => {
    "use strict";

    const header = document.querySelector("[data-v3-header]");
    const progress = document.querySelector("[data-v3-progress]");
    const dock = document.querySelector("[data-v3-dock]");
    if (!header || !progress || !dock) return;

    let scheduled = false;

    const update = () => {
        const top = window.scrollY || document.documentElement.scrollTop;
        const maximum = Math.max(document.documentElement.scrollHeight - window.innerHeight, 1);
        const value = Math.min(Math.max(top / maximum, 0), 1);
        header.classList.toggle("is-compact", top > 28);
        progress.style.setProperty("--v3-progress", String(value));
        scheduled = false;
    };

    const requestUpdate = () => {
        if (scheduled) return;
        scheduled = true;
        window.requestAnimationFrame(update);
    };

    window.addEventListener("scroll", requestUpdate, { passive: true });
    window.addEventListener("resize", requestUpdate, { passive: true });
    update();
})();
