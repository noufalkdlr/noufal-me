"""
build.py — Static site build script.

Run from the project root:
    python build/build.py

Output goes to dist/:
    dist/index.html
    dist/blogs/index.html
    dist/blogs/<slug>/index.html
    dist/static/...

Renders plain HTML templates using two tiny mechanisms:
  - {{ include:file.html }}   → inlines a partial from templates/
  - {{ key }}                 → simple string substitution
  - {{ each:categories }}...{{ /each }} → repeats a block per category
Blog posts are Markdown files with YAML-ish frontmatter in content/blogs/.
"""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
CONTENT_BLOGS = ROOT / "content" / "blogs"
DIST = ROOT / "dist"

INCLUDE_PATTERN = re.compile(r"\{\{\s*include:([\w.\-]+)\s*\}\}")
EACH_PATTERN = re.compile(
    r"\{\{\s*each:categories\s*\}\}(.*?)\{\{\s*/each\s*\}\}", re.DOTALL
)


def clean_dist() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)


def copy_static() -> None:
    dist_static = DIST / "static"
    shutil.copytree(STATIC, dist_static)


def render_includes(html: str) -> str:
    """Replace {{ include:filename.html }} with the contents of that
    file from templates/. Partial filenames should start with an
    underscore, e.g. _footer.html."""

    def replace(match: re.Match) -> str:
        partial_path = TEMPLATES / match.group(1)
        return partial_path.read_text(encoding="utf-8")

    return INCLUDE_PATTERN.sub(replace, html)


def render_vars(html: str, context: dict) -> str:
    for key, value in context.items():
        html = html.replace("{{ " + key + " }}", str(value))
    return html


# --- Blog content parsing -------------------------------------------------


def parse_frontmatter(raw: str) -> tuple[dict, str]:
    """Split a markdown file into (frontmatter dict, body). Frontmatter
    is the simple `key: value` block between --- lines, with basic
    support for `tags:` as a YAML-style list."""

    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw

    fm_raw, body = parts[1], parts[2]
    meta: dict = {}
    current_list_key = None

    for line in fm_raw.strip().splitlines():
        if line.strip().startswith("- ") and current_list_key:
            meta.setdefault(current_list_key, []).append(line.strip()[2:].strip())
            continue

        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value == "":
                current_list_key = key
                meta[key] = []
            else:
                current_list_key = None
                meta[key] = value

    return meta, body.strip()


def format_date(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%B %-d, %Y")
    except ValueError:
        return date_str


def load_blogs() -> list[dict]:
    blogs = []
    for md_file in sorted(CONTENT_BLOGS.glob("*.md")):
        raw = md_file.read_text(encoding="utf-8")
        if not raw.strip():
            continue

        meta, body = parse_frontmatter(raw)
        slug = md_file.stem
        html_content = markdown.markdown(body, extensions=["fenced_code", "tables"])

        thumbnail = meta.get("thumbnail", "")
        if thumbnail.startswith("/") and not thumbnail.startswith("/static/"):
            thumbnail = "/static" + thumbnail

        blogs.append(
            {
                "slug": slug,
                "title": meta.get("title", slug),
                "date": meta.get("date", ""),
                "formatted_date": format_date(meta.get("date", "")),
                "description": meta.get("description", ""),
                "author": meta.get("author", "Mohammed Noufal"),
                "thumbnail": thumbnail,
                "category": meta.get("category", "Uncategorized"),
                "tags": meta.get("tags", []),
                "content_html": html_content,
            }
        )

    blogs.sort(key=lambda b: b["date"], reverse=True)
    return blogs


# --- Page builders ----------------------------------------------------------


def build_home_page() -> None:
    src = TEMPLATES / "index.html"
    dst = DIST / "index.html"
    html = src.read_text(encoding="utf-8")
    html = render_includes(html)
    dst.write_text(html, encoding="utf-8")


def build_blogs_index(blogs: list[dict]) -> None:
    src = TEMPLATES / "blogs_index.html"
    html = src.read_text(encoding="utf-8")
    html = render_includes(html)

    categories = sorted({b["category"] for b in blogs})

    def each_replace(match: re.Match) -> str:
        block = match.group(1)
        return "".join(block.replace("{{ category }}", cat) for cat in categories)

    html = EACH_PATTERN.sub(each_replace, html)

    blogs_json = json.dumps(
        [
            {
                "slug": b["slug"],
                "title": b["title"],
                "formatted_date": b["formatted_date"],
                "description": b["description"],
                "thumbnail": b["thumbnail"],
                "category": b["category"],
                "tags": b["tags"],
            }
            for b in blogs
        ]
    )
    html = render_vars(html, {"blogs_json": blogs_json})

    out_dir = DIST / "blogs"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html, encoding="utf-8")


def build_blog_detail_pages(blogs: list[dict]) -> None:
    src = TEMPLATES / "blog_detail.html"
    template = src.read_text(encoding="utf-8")

    for blog in blogs:
        html = render_includes(template)
        html = render_vars(
            html,
            {
                "title": blog["title"],
                "description": blog["description"],
                "author": blog["author"],
                "date": blog["date"],
                "formatted_date": blog["formatted_date"],
                "category": blog["category"],
                "thumbnail": blog["thumbnail"],
                "slug": blog["slug"],
                "content": blog["content_html"],
            },
        )

        out_dir = DIST / "blogs" / blog["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(html, encoding="utf-8")


def build_robots_txt() -> None:
    src = ROOT / "robots.txt"
    if src.exists():
        shutil.copy(src, DIST / "robots.txt")


def build_sitemap(blogs: list[dict]) -> None:
    base = "https://noufal.me"
    today = datetime.now().strftime("%Y-%m-%d")

    urls = [
        {"loc": f"{base}/", "lastmod": today, "priority": "1.0"},
        {"loc": f"{base}/blogs/", "lastmod": today, "priority": "0.8"},
    ]
    for b in blogs:
        urls.append(
            {
                "loc": f"{base}/blogs/{b['slug']}/",
                "lastmod": b["date"] or today,
                "priority": "0.6",
            }
        )

    entries = "\n".join(
        f"  <url>\n"
        f"    <loc>{u['loc']}</loc>\n"
        f"    <lastmod>{u['lastmod']}</lastmod>\n"
        f"    <priority>{u['priority']}</priority>\n"
        f"  </url>"
        for u in urls
    )

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>\n"
    )

    (DIST / "sitemap.xml").write_text(xml, encoding="utf-8")


def main() -> None:
    clean_dist()
    copy_static()
    build_home_page()
    build_robots_txt()

    blogs = load_blogs()
    build_blogs_index(blogs)
    build_blog_detail_pages(blogs)
    build_sitemap(blogs)

    print(f"Build complete → {DIST} ({len(blogs)} blog posts)")


if __name__ == "__main__":
    main()
