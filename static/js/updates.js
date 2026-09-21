(() => {
  "use strict";
  const form = document.querySelector("[data-updates-filters]");
  const list = document.querySelector("[data-update-list]");
  if (!form || !list) return;
  const search = form.querySelector("[data-update-search]");
  const status = form.querySelector("[data-update-status]");
  const category = form.querySelector("[data-update-category]");
  const count = document.querySelector("[data-update-count]");
  const empty = document.querySelector("[data-update-empty]");
  const items = Array.from(list.querySelectorAll("[data-update-item]"));
  const normalize = (value) => value.trim().toLocaleLowerCase(document.documentElement.lang);
  const apply = () => {
    const query = normalize(search.value);
    let visible = 0;
    items.forEach((item) => {
      const matches = (!query || normalize(item.dataset.search).includes(query)) && (!status.value || item.dataset.status === status.value) && (!category.value || item.dataset.category === category.value);
      item.hidden = !matches;
      if (matches) visible += 1;
    });
    count.textContent = String(visible);
    empty.hidden = visible !== 0;
    const parameters = new URLSearchParams();
    if (search.value.trim()) parameters.set("q", search.value.trim());
    if (status.value) parameters.set("status", status.value);
    if (category.value) parameters.set("category", category.value);
    const suffix = parameters.toString();
    history.replaceState(null, "", `${location.pathname}${suffix ? `?${suffix}` : ""}`);
  };
  form.addEventListener("submit", (event) => { event.preventDefault(); apply(); });
  search.addEventListener("input", apply);
  status.addEventListener("change", apply);
  category.addEventListener("change", apply);
})();
