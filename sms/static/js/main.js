document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.querySelector(".navbar-toggle");
  const links = document.querySelector(".navbar-links");
  toggle.addEventListener("click", () => {
    links.classList.toggle("show");
  });
});