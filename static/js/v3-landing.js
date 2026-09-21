(() => {
    "use strict";
    const root = document.querySelector("[data-v3-landing]");
    if (!root) return;
    const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const coarse = matchMedia("(pointer: coarse)").matches;
    const reveal = document.querySelectorAll("[data-v3-reveal]");
    if (reduced) {
        reveal.forEach((item) => item.classList.add("is-visible"));
    } else {
        const observer = new IntersectionObserver((entries) => entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("is-visible");
                observer.unobserve(entry.target);
            }
        }), { threshold: 0.14 });
        reveal.forEach((item) => observer.observe(item));
    }
    document.querySelectorAll(".v3-portal-card").forEach((card) => card.addEventListener("pointermove", (event) => {
        if (coarse || reduced) return;
        const rectangle = card.getBoundingClientRect();
        card.style.setProperty("--px", `${event.clientX - rectangle.left}px`);
        card.style.setProperty("--py", `${event.clientY - rectangle.top}px`);
    }));
    if (!coarse && !reduced) {
        const hero = document.querySelector("[data-v3-hero]");
        hero?.addEventListener("pointermove", (event) => {
            const x = event.clientX / innerWidth - 0.5;
            const y = event.clientY / innerHeight - 0.5;
            hero.querySelectorAll("[data-v3-depth]").forEach((layer) => {
                const depth = Number(layer.dataset.v3Depth || 0);
                layer.style.transform = `translate3d(${x * depth * 18}px, ${y * depth * 14}px, 0)`;
            });
        });
    }
    const canvas = document.querySelector("[data-v3-neural-canvas]");
    if (!canvas || reduced) return;
    const context = canvas.getContext("2d");
    let width = 0;
    let height = 0;
    let visible = true;
    const points = Array.from({ length: innerWidth < 700 ? 22 : 40 }, () => ({
        x: Math.random(), y: Math.random(), vx: (Math.random() - 0.5) * 0.00012, vy: (Math.random() - 0.5) * 0.00012,
    }));
    const resize = () => {
        const rectangle = canvas.getBoundingClientRect();
        const ratio = Math.min(devicePixelRatio || 1, 1.5);
        width = rectangle.width;
        height = rectangle.height;
        canvas.width = width * ratio;
        canvas.height = height * ratio;
        context.setTransform(ratio, 0, 0, ratio, 0, 0);
    };
    const draw = () => {
        requestAnimationFrame(draw);
        if (!visible || document.hidden) return;
        context.clearRect(0, 0, width, height);
        points.forEach((point, index) => {
            point.x += point.vx;
            point.y += point.vy;
            if (point.x < 0 || point.x > 1) point.vx *= -1;
            if (point.y < 0 || point.y > 1) point.vy *= -1;
            context.fillStyle = "rgba(111,255,164,.62)";
            context.fillRect(point.x * width, point.y * height, 1.5, 1.5);
            for (let next = index + 1; next < points.length; next += 1) {
                const other = points[next];
                const distance = Math.hypot((point.x - other.x) * width, (point.y - other.y) * height);
                if (distance < 105) {
                    context.strokeStyle = `rgba(57,255,136,${(1 - distance / 105) * 0.21})`;
                    context.beginPath();
                    context.moveTo(point.x * width, point.y * height);
                    context.lineTo(other.x * width, other.y * height);
                    context.stroke();
                }
            }
        });
    };
    new IntersectionObserver((entries) => { visible = entries[0].isIntersecting; }, { threshold: 0.05 }).observe(canvas);
    addEventListener("resize", resize, { passive: true });
    resize();
    requestAnimationFrame(draw);
})();
