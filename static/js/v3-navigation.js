(() => {
    "use strict";

    const STORAGE_KEY = "ivanllopis.v3.visited.v1";
    const order = ["home", "technologies", "projects", "work-life", "hobbies", "talent"];
    const header = document.querySelector("[data-v3-header]");
    const dock = document.querySelector("[data-v3-dock]");
    const progress = document.querySelector("[data-v3-progress]");
    const current = document.body.dataset.v3Page || "home";
    const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!header || !dock || !progress) return;

    const transitionKey = "ivanllopis.v3.transition.v1";
    try {
        if (sessionStorage.getItem(transitionKey) === "active" && !reducedMotion) {
            document.body.classList.add("v3-glitch-enter");
            sessionStorage.removeItem(transitionKey);
            window.setTimeout(() => document.body.classList.remove("v3-glitch-enter"), 380);
        }
    } catch {
        document.body.classList.remove("v3-glitch-enter");
    }

    const readVisited = () => {
        try {
            const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
            return Array.isArray(saved) ? saved.filter((item) => order.includes(item)) : [];
        } catch {
            return [];
        }
    };

    const writeVisited = (visited) => {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(visited));
        } catch {
            return false;
        }
        return true;
    };

    const visited = readVisited();
    if (order.includes(current) && !visited.includes(current)) {
        visited.push(current);
        writeVisited(visited);
    }

    const nextSuggested = order.find((item) => !visited.includes(item));
    document.documentElement.style.setProperty("--v3-visited-count", String(visited.length));
    document.querySelectorAll("[data-v3-destination]").forEach((link) => {
        const destination = link.dataset.v3Destination;
        link.classList.toggle("is-visited", visited.includes(destination));
        link.classList.toggle("is-suggested", destination === nextSuggested);
    });

    document.querySelectorAll(".v3-nav-rail, .v3-dock-rail").forEach((rail) => {
        [...rail.querySelectorAll("i")].forEach((segment, index) => {
            const leftVisited = visited.includes(order[index]);
            const rightVisited = visited.includes(order[index + 1]);
            segment.classList.toggle("is-connected", leftVisited && rightVisited);
        });
    });

    let scheduled = false;
    const update = () => {
        const top = window.scrollY || document.documentElement.scrollTop;
        const maximum = Math.max(document.documentElement.scrollHeight - window.innerHeight, 1);
        header.classList.toggle("is-compact", top > 28);
        progress.style.setProperty("--v3-progress", String(Math.min(Math.max(top / maximum, 0), 1)));
        scheduled = false;
    };
    const requestUpdate = () => {
        if (scheduled) return;
        scheduled = true;
        requestAnimationFrame(update);
    };

    const matrixBurst = (canvas) => {
        if (reducedMotion || !canvas) return;
        const context = canvas.getContext("2d");
        const rectangle = canvas.getBoundingClientRect();
        const ratio = Math.min(devicePixelRatio || 1, 2);
        canvas.width = Math.max(1, Math.round(rectangle.width * ratio));
        canvas.height = Math.max(1, Math.round(rectangle.height * ratio));
        context.setTransform(ratio, 0, 0, ratio, 0, 0);
        const fontSize = rectangle.height < 90 ? 10 : 12;
        const columns = Math.max(8, Math.floor(rectangle.width / 22));
        const drops = Array.from({ length: columns }, (_, index) => ({
            x: index * (rectangle.width / columns),
            y: -Math.random() * rectangle.height,
            speed: 1.7 + Math.random() * 2.5,
        }));
        const started = performance.now();
        canvas.classList.add("is-active");
        const draw = (now) => {
            const elapsed = now - started;
            context.clearRect(0, 0, rectangle.width, rectangle.height);
            context.font = `${fontSize}px ui-monospace, monospace`;
            drops.forEach((drop) => {
                drop.y += drop.speed;
                context.globalAlpha = Math.max(0, 0.82 - elapsed / 520);
                context.fillStyle = "#62ff9d";
                context.fillText(Math.random() > 0.5 ? "1" : "0", drop.x, drop.y);
                if (drop.y > rectangle.height + 10) drop.y = -12;
            });
            if (elapsed < 430) {
                requestAnimationFrame(draw);
            } else {
                context.clearRect(0, 0, rectangle.width, rectangle.height);
                canvas.classList.remove("is-active");
            }
        };
        requestAnimationFrame(draw);
    };

    document.querySelectorAll("a[data-v3-destination]").forEach((link) => {
        link.addEventListener("click", (event) => {
            if (event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
            const destination = link.dataset.v3Destination;
            if (destination === current || reducedMotion) return;
            event.preventDefault();
            document.querySelectorAll(`[data-v3-destination="${destination}"]`).forEach((match) => match.classList.add("is-activating"));
            document.body.classList.add("v3-glitch-exit");
            try {
                sessionStorage.setItem(transitionKey, "active");
            } catch {
                document.body.classList.remove("v3-glitch-enter");
            }
            const container = link.closest("[data-v3-header], [data-v3-dock]");
            matrixBurst(container?.querySelector("[data-v3-nav-matrix]"));
            window.setTimeout(() => location.assign(link.href), window.innerWidth <= 760 ? 145 : 210);
        });
    });

    window.addEventListener("scroll", requestUpdate, { passive: true });
    window.addEventListener("resize", requestUpdate, { passive: true });
    update();
})();
