(() => {
    "use strict";

    const toggle = document.getElementById("ai-toggle");
    const shell = document.getElementById("ai-chat-shell");
    const panel = document.getElementById("ai-panel");
    const closeButton = document.getElementById("ai-close");
    const form = document.getElementById("ai-form");
    const input = document.getElementById("ai-input");
    const messages = document.getElementById("ai-messages");

    if (!toggle || !shell || !panel || !closeButton || !form || !input || !messages) {
        return;
    }

    const history = [];
    let requestInProgress = false;

    const setExpanded = (expanded) => {
        shell.hidden = !expanded;
        toggle.setAttribute("aria-expanded", String(expanded));

        if (expanded) {
            window.requestAnimationFrame(() => input.focus());
        } else {
            toggle.focus();
        }
    };

    const addMessage = (text, className = "") => {
        const item = document.createElement("p");
        item.textContent = text;
        if (className) {
            item.className = className;
        }
        messages.appendChild(item);
        messages.scrollTop = messages.scrollHeight;
        return item;
    };

    const resizeInput = () => {
        input.style.height = "auto";
        input.style.height = `${Math.min(input.scrollHeight, 110)}px`;
    };

    const setLoading = (loading) => {
        requestInProgress = loading;
        input.disabled = loading;
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = loading;
            submitButton.textContent = loading ? "..." : "Enviar";
        }
    };

    const openAssistant = () => setExpanded(true);
    const closeAssistant = () => setExpanded(false);

    toggle.addEventListener("click", openAssistant);
    closeButton.addEventListener("click", closeAssistant);

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !shell.hidden) {
            closeAssistant();
        }
    });

    input.addEventListener("input", resizeInput);

    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            form.requestSubmit();
        }
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (requestInProgress) {
            return;
        }

        const message = input.value.trim();
        if (!message) {
            input.focus();
            return;
        }

        addMessage(message, "ai-user");
        input.value = "";
        resizeInput();
        setLoading(true);

        const pendingMessage = addMessage("Pensando...");

        try {
            const response = await fetch("/api/assistant/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    message,
                    history: history.slice(-6),
                    language: document.documentElement.lang || "es",
                }),
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || "No se pudo obtener una respuesta.");
            }

            pendingMessage.textContent = data.answer;
            history.push(
                { role: "user", content: message },
                { role: "assistant", content: data.answer },
            );
        } catch (error) {
            pendingMessage.textContent =
                error instanceof Error
                    ? error.message
                    : "No se pudo obtener una respuesta.";
            pendingMessage.classList.add("ai-error");
        } finally {
            setLoading(false);
            input.focus();
        }
    });

    resizeInput();
    setExpanded(false);
})();
