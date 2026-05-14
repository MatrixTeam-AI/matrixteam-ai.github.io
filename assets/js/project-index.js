(function () {
  var grid = document.getElementById("project-index-grid");
  var empty = document.getElementById("project-index-empty");
  var updated = document.getElementById("project-index-updated");

  if (!grid) return;

  function escapeHtml(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function projectInitials(title) {
    return String(title || "Project")
      .split(/[\s:.-]+/)
      .filter(Boolean)
      .slice(0, 2)
      .map(function (word) { return word.charAt(0).toUpperCase(); })
      .join("");
  }

  function card(project) {
    var image = project.image
      ? '<div class="project-card-media"><img src="' + escapeHtml(project.image) + '" alt=""></div>'
      : '<div class="project-card-media project-card-fallback"><span>' + escapeHtml(projectInitials(project.title)) + "</span></div>";
    var tags = Array.isArray(project.tags) && project.tags.length
      ? '<div class="project-tags">' + project.tags.slice(0, 4).map(function (tag) {
          return "<span>" + escapeHtml(tag) + "</span>";
        }).join("") + "</div>"
      : "";
    var status = project.status ? '<span class="project-status">' + escapeHtml(project.status) + "</span>" : "";

    return [
      '<article class="project-card wow fadeInUp animated">',
      '  <a href="' + escapeHtml(project.url) + '" aria-label="Open ' + escapeHtml(project.title) + '">',
      image,
      '    <div class="project-card-body">',
      '      <div class="project-card-meta"><span>' + escapeHtml(project.slug) + "</span>" + status + "</div>",
      '      <h3>' + escapeHtml(project.title) + "</h3>",
      '      <p>' + escapeHtml(project.description) + "</p>",
      tags,
      '      <span class="project-card-link">Open project <i class="fa fa-angle-right"></i></span>',
      "    </div>",
      "  </a>",
      "</article>",
    ].join("");
  }

  function render(data) {
    var projects = Array.isArray(data.projects) ? data.projects : [];
    if (!projects.length) {
      if (empty) empty.style.display = "block";
      return;
    }
    grid.innerHTML = projects.map(card).join("");
    if (updated && data.generatedAt) {
      updated.textContent = "Updated " + data.generatedAt.slice(0, 10);
    }
  }

  if (window.MATRIX_PROJECT_INDEX) {
    render(window.MATRIX_PROJECT_INDEX);
    return;
  }

  fetch("assets/data/projects.json", { cache: "no-cache" })
    .then(function (response) {
      if (!response.ok) throw new Error("Unable to load project index");
      return response.json();
    })
    .then(render)
    .catch(function () {
      if (empty) empty.style.display = "block";
      grid.innerHTML = "";
    });
})();
