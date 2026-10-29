// Menu mobile
(function () {
  const btn = document.querySelector(".nav__toggle");
  const menu = document.getElementById("menu");
  if (!btn || !menu) return;
  btn.addEventListener("click", () => {
    const open = menu.classList.toggle("is-open");
    btn.setAttribute("aria-expanded", open);
  });
  menu.addEventListener("click", (e) => {
    if (e.target.closest("a")) {
      menu.classList.remove("is-open");
      btn.setAttribute("aria-expanded", "false");
    }
  });
})();

// Cartes de projet : légère inclinaison 3D qui suit le pointeur (souris uniquement).
(function () {
  const fine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!fine || reduce) return;
  const MAX = 6; // degrés
  document.querySelectorAll(".card").forEach((card) => {
    card.addEventListener("pointermove", (e) => {
      const r = card.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width;
      const y = (e.clientY - r.top) / r.height;
      card.classList.add("is-tilting");
      card.style.setProperty("--ry", `${(x - 0.5) * MAX * 2}deg`);
      card.style.setProperty("--rx", `${(0.5 - y) * MAX * 2}deg`);
      card.style.setProperty("--mx", `${x * 100}%`);
      card.style.setProperty("--my", `${y * 100}%`);
    });
    card.addEventListener("pointerleave", () => {
      card.classList.remove("is-tilting");
      card.style.setProperty("--rx", "0deg");
      card.style.setProperty("--ry", "0deg");
    });
  });
})();

// Adresse e-mail : reconstituée ici pour ne pas figurer en clair dans le HTML.
document.querySelectorAll(".js-email").forEach((lien) => {
  try {
    const adresse = atob(lien.dataset.e).split("").reverse().join("");
    lien.href = `mailto:${adresse}`;
    if (lien.hasAttribute("data-texte")) lien.textContent = adresse;
  } catch {
    // En cas d'échec, le lien continue de mener au formulaire de contact.
  }
});
