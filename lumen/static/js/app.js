/* No inline scripts (strict CSP). Everything user-supplied is HTML-escaped BEFORE formatting. */
(function () {
  "use strict";
  function esc(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }
  function inline(s) {
    return s.replace(/`([^`]+)`/g, "<code>$1</code>")
            .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
            .replace(/(^|[^*])\*([^*\s][^*]*)\*/g, "$1<em>$2</em>");
  }
  function render(text) {
    return esc(text).split(/\n{2,}/).map(function (block) {
      var lines = block.split("\n");
      if (lines.every(function (l) { return /^\s*[-*] /.test(l); })) {
        return "<ul>" + lines.map(function (l) { return "<li>" + inline(l.replace(/^\s*[-*] /, "")) + "</li>"; }).join("") + "</ul>";
      }
      if (/^#{1,3} /.test(block)) { return "<h3>" + inline(block.replace(/^#{1,3} /, "")) + "</h3>"; }
      return "<p>" + inline(lines.join("<br>")) + "</p>";
    }).join("");
  }
  document.querySelectorAll("[data-md]").forEach(function (el) {
    el.innerHTML = render(el.textContent);
    el.classList.add("rendered");
  });
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!window.confirm(form.getAttribute("data-confirm"))) { e.preventDefault(); }
    });
  });
  document.querySelectorAll("textarea[data-counter]").forEach(function (ta) {
    var out = document.querySelector(ta.getAttribute("data-counter"));
    var max = parseInt(ta.getAttribute("maxlength"), 10);
    function update() { out.textContent = ta.value.length + " / " + max + " characters"; }
    ta.addEventListener("input", update); update();
  });
})();
