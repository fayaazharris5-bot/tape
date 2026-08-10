/* Generates sitemap.xml and robots.txt from the term list in index.html.
   Run:  node sitemap.js https://USERNAME.github.io/tape
   No dependencies, no network. */
const fs = require("fs");
const base = (process.argv[2] || "").replace(/\/+$/, "");
if (!base) {
  console.error("usage: node sitemap.js https://your-site-url");
  process.exit(1);
}

const html = fs.readFileSync("index.html", "utf8");
const slugs = new Set();
const re = /\{t:"((?:[^"\\]|\\.)*)",c:"[a-z0-9]+"/g;
let m;
while ((m = re.exec(html))) {
  slugs.add(m[1].toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, ""));
}

const today = new Date().toISOString().slice(0, 10);
const urls = [base + "/"].concat([...slugs].map(s => base + "/#t=" + s));
const xml =
  '<?xml version="1.0" encoding="UTF-8"?>\n' +
  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
  urls
    .map(u => "  <url><loc>" + u.replace(/&/g, "&amp;") + "</loc><lastmod>" + today + "</lastmod></url>")
    .join("\n") +
  "\n</urlset>\n";

fs.writeFileSync("sitemap.xml", xml);
fs.writeFileSync("robots.txt", "User-agent: *\nAllow: /\nSitemap: " + base + "/sitemap.xml\n");
console.log("wrote sitemap.xml (" + urls.length + " urls) and robots.txt for " + base);
