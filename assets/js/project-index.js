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

  function formatProjectDate(value) {
    var text = String(value || "").trim();
    var match = text.match(/^(\d{4}-\d{2}-\d{2})/);
    return match ? match[1] : text;
  }

  function projectTimestamp(project) {
    var date = formatProjectDate(project && project.updatedAt);
    if (!date) return 0;
    var timestamp = Date.parse(date + "T00:00:00Z");
    return Number.isNaN(timestamp) ? 0 : timestamp;
  }

  function sortProjects(projects) {
    return projects.slice().sort(function (a, b) {
      var byDate = projectTimestamp(b) - projectTimestamp(a);
      return byDate || 0;
    });
  }

  function projectImage(project) {
    var alt = escapeHtml(project.title) + " cover";
    var img = '<img src="' + escapeHtml(project.image) + '" alt="' + alt + '" loading="lazy" decoding="async" fetchpriority="low" width="960" height="540">';
    if (!project.imageWebp) return img;
    return [
      "<picture>",
      '  <source srcset="' + escapeHtml(project.imageWebp) + '" type="image/webp">',
      "  " + img,
      "</picture>",
    ].join("");
  }

  function card(project) {
    var image = project.image
      ? '<div class="project-card-media">' + projectImage(project) + "</div>"
      : '<div class="project-card-media project-card-fallback"><span>' + escapeHtml(projectInitials(project.title)) + "</span></div>";
    var tags = Array.isArray(project.tags) && project.tags.length
      ? '<div class="project-tags">' + project.tags.slice(0, 4).map(function (tag) {
          return "<span>" + escapeHtml(tag) + "</span>";
        }).join("") + "</div>"
      : "";
    var status = project.status ? '<span class="project-status">' + escapeHtml(project.status) + "</span>" : "";
    var updatedAt = formatProjectDate(project.updatedAt);
    var date = updatedAt
      ? '<time class="project-date" datetime="' + escapeHtml(updatedAt) + '" aria-label="Updated ' + escapeHtml(updatedAt) + '">' + escapeHtml(updatedAt) + "</time>"
      : "";
    var badges = status || date
      ? '<span class="project-card-badges">' + status + date + "</span>"
      : "";

    return [
      '<article class="project-card wow fadeInUp animated">',
      '  <a href="' + escapeHtml(project.url) + '" aria-label="Open ' + escapeHtml(project.title) + '">',
      image,
      '    <div class="project-card-body">',
      '      <div class="project-card-meta"><span class="project-slug">' + escapeHtml(project.slug) + "</span>" + badges + "</div>",
      '      <h3>' + escapeHtml(project.title) + "</h3>",
      '      <p>' + escapeHtml(project.description) + "</p>",
      '      <div class="project-card-footer">',
      tags,
      '        <span class="project-card-link">Open project <i class="fa fa-angle-right"></i></span>',
      "      </div>",
      "    </div>",
      "  </a>",
      "</article>",
    ].join("");
  }

  function render(data) {
    var projects = Array.isArray(data.projects) ? sortProjects(data.projects) : [];
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
