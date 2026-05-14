#!/usr/bin/env node

import { promises as fs } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const siteRoot = path.resolve(scriptDir, "..");
const pagesDir = path.join(siteRoot, "pages");
const outputFile = path.join(siteRoot, "assets", "data", "projects.json");
const outputScriptFile = path.join(siteRoot, "assets", "data", "projects.js");

const MAX_DESCRIPTION_LENGTH = 260;

function decodeEntities(value) {
  return value
    .replace(/&nbsp;/gi, " ")
    .replace(/&amp;/gi, "&")
    .replace(/&quot;/gi, '"')
    .replace(/&#39;/gi, "'")
    .replace(/&lt;/gi, "<")
    .replace(/&gt;/gi, ">");
}

function stripHtml(value) {
  return decodeEntities(value.replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim());
}

function stripMarkdown(value) {
  return value
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/!\[[^\]]*]\([^)]*\)/g, " ")
    .replace(/\[([^\]]+)]\([^)]*\)/g, "$1")
    .replace(/[#>*_~|-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function compact(value) {
  return decodeEntities(String(value || "").replace(/\s+/g, " ").trim());
}

function truncate(value, length = MAX_DESCRIPTION_LENGTH) {
  const text = compact(value);
  if (text.length <= length) return text;
  const clipped = text.slice(0, length - 1);
  const boundary = clipped.lastIndexOf(" ");
  return `${clipped.slice(0, boundary > 120 ? boundary : clipped.length).trim()}...`;
}

function pickMeta(html, names) {
  for (const name of names) {
    const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const patterns = [
      new RegExp(`<meta\\s+[^>]*(?:name|property)=["']${escaped}["'][^>]*content=["']([^"']+)["'][^>]*>`, "i"),
      new RegExp(`<meta\\s+[^>]*content=["']([^"']+)["'][^>]*(?:name|property)=["']${escaped}["'][^>]*>`, "i"),
    ];
    for (const pattern of patterns) {
      const match = html.match(pattern);
      if (match?.[1]) return compact(match[1]);
    }
  }
  return "";
}

function pickHtmlTitle(html) {
  return compact(
    pickMeta(html, ["og:title", "twitter:title", "citation_title"])
    || html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1]
    || html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i)?.[1]
    || "",
  );
}

function pickHtmlDescription(html) {
  const fromMeta = pickMeta(html, ["description", "og:description", "twitter:description"]);
  if (fromMeta) return truncate(fromMeta);

  const paragraphs = [...html.matchAll(/<p[^>]*>([\s\S]*?)<\/p>/gi)]
    .map((match) => stripHtml(match[1]))
    .filter((text) => text.length > 80 && !/copyright|equal contribution/i.test(text));
  return truncate(paragraphs[0] || "");
}

function pickHtmlImage(html, slug) {
  const image = pickMeta(html, ["og:image", "twitter:image"]);
  if (!image || /^https?:\/\//i.test(image) || image.startsWith("data:")) return image;
  return normalizeProjectPath(image, slug);
}

function normalizeProjectPath(value, slug) {
  if (!value || /^https?:\/\//i.test(value) || value.startsWith("data:")) {
    return value || "";
  }
  const cleaned = value.replace(/^\/+/, "").replace(/^\.\//, "");
  if (cleaned.startsWith("assets/") || cleaned.startsWith("pages/")) return cleaned;
  return `pages/${slug}/${cleaned}`;
}

function normalizeProjectUrl(value, slug) {
  if (!value) return `pages/${slug}/`;
  if (/^https?:\/\//i.test(value) || value.startsWith("mailto:")) return value;
  return value.replace(/^\/+/, "");
}

function pickReadmeTitle(markdown) {
  const heading = markdown.match(/^#\s+(.+)$/m)?.[1];
  return compact(heading || "");
}

function pickReadmeDescription(markdown) {
  const withoutTitle = markdown.replace(/^#\s+.+$/m, "");
  const paragraphs = withoutTitle
    .split(/\n\s*\n/g)
    .map(stripMarkdown)
    .filter((text) => text.length > 80 && !/^structure$/i.test(text));
  return truncate(paragraphs[0] || "");
}

function titleFromSlug(slug) {
  return slug
    .replace(/[-_]+/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

async function readTextIfExists(file) {
  try {
    return await fs.readFile(file, "utf8");
  } catch (error) {
    if (error.code === "ENOENT") return "";
    throw error;
  }
}

async function readJsonIfExists(file) {
  const text = await readTextIfExists(file);
  if (!text) return {};
  return JSON.parse(text);
}

async function projectFromDirectory(dirent) {
  const slug = dirent.name;
  const projectDir = path.join(pagesDir, slug);
  const [custom, html, readme, stats] = await Promise.all([
    readJsonIfExists(path.join(projectDir, "project.json")),
    readTextIfExists(path.join(projectDir, "index.html")),
    readTextIfExists(path.join(projectDir, "README.md")),
    fs.stat(projectDir),
  ]);

  const htmlTitle = html ? stripHtml(pickHtmlTitle(html)) : "";
  const readmeTitle = readme ? pickReadmeTitle(readme) : "";
  const htmlDescription = html ? pickHtmlDescription(html) : "";
  const readmeDescription = readme ? pickReadmeDescription(readme) : "";
  const image = custom.image ? normalizeProjectPath(custom.image, slug) : (html ? pickHtmlImage(html, slug) : "");

  return {
    slug,
    title: compact(custom.title || htmlTitle || readmeTitle || titleFromSlug(slug)),
    description: truncate(custom.description || htmlDescription || readmeDescription || "Project page from Matrix Team."),
    url: normalizeProjectUrl(custom.url, slug),
    image: image || "",
    status: custom.status || "",
    tags: Array.isArray(custom.tags) ? custom.tags : [],
    updatedAt: custom.updatedAt || stats.mtime.toISOString().slice(0, 10),
  };
}

async function main() {
  const entries = await fs.readdir(pagesDir, { withFileTypes: true });
  const directories = entries
    .filter((entry) => entry.isDirectory() && !entry.name.startsWith("."))
    .sort((a, b) => a.name.localeCompare(b.name));

  const projectDirectories = (await Promise.all(directories.map(async (entry) => {
    const projectDir = path.join(pagesDir, entry.name);
    const hasIndex = Boolean(await readTextIfExists(path.join(projectDir, "index.html")));
    const hasConfig = Boolean(await readTextIfExists(path.join(projectDir, "project.json")));
    return hasIndex || hasConfig ? entry : null;
  }))).filter(Boolean);

  const projects = await Promise.all(projectDirectories.map(projectFromDirectory));
  projects.sort((a, b) => b.updatedAt.localeCompare(a.updatedAt) || a.title.localeCompare(b.title));

  const payload = {
    generatedAt: new Date().toISOString(),
    source: "scripts/generate-project-index.mjs",
    projects,
  };

  await fs.mkdir(path.dirname(outputFile), { recursive: true });
  await fs.writeFile(outputFile, `${JSON.stringify(payload, null, 2)}\n`);
  await fs.writeFile(
    outputScriptFile,
    `window.MATRIX_PROJECT_INDEX = ${JSON.stringify(payload, null, 2)};\n`,
  );
  console.log(`Generated ${path.relative(siteRoot, outputFile)} and ${path.relative(siteRoot, outputScriptFile)} with ${projects.length} projects.`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
