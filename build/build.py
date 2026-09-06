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
import struct
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


def iso_date(date_str: str) -> str:
    """Full ISO 8601 datetime with timezone, for JSON-LD datePublished."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%dT00:00:00+00:00")
    except ValueError:
        return date_str


def get_webp_dimensions(path: Path) -> tuple[int, int]:
    """Read width/height from a WebP file header without extra deps."""
    try:
        with open(path, "rb") as f:
            header = f.read(30)
        if header[0:4] != b"RIFF" or header[8:12] != b"WEBP":
            return (0, 0)
        chunk = header[12:16]
        if chunk == b"VP8 ":
            w, h = struct.unpack("<HH", header[26:30])
            return (w & 0x3FFF, h & 0x3FFF)
        if chunk == b"VP8L":
            b0, b1, b2, b3 = header[21:25]
            w = 1 + (((b1 & 0x3F) << 8) | b0)
            h = 1 + (((b3 & 0xF) << 10) | (b2 << 2) | (b1 >> 6))
            return (w, h)
        if chunk == b"VP8X":
            w = 1 + (header[24] | (header[25] << 8) | (header[26] << 16))
            h = 1 + (header[27] | (header[28] << 8) | (header[29] << 16))
            return (w, h)
    except (OSError, struct.error, IndexError):
        pass
    return (0, 0)


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

        thumb_path = STATIC / thumbnail.removeprefix("/static/") if thumbnail else None
        img_w, img_h = (
            get_webp_dimensions(thumb_path)
            if thumb_path and thumb_path.exists()
            else (0, 0)
        )

        blogs.append(
            {
                "slug": slug,
                "title": meta.get("title", slug),
                "date": meta.get("date", ""),
                "formatted_date": format_date(meta.get("date", "")),
                "description": meta.get("description", ""),
                "author": meta.get("author", "Mohammed Noufal"),
                "thumbnail": thumbnail,
                "image_width": img_w or 1200,
                "image_height": img_h or 630,
                "category": meta.get("category", "Uncategorized"),
                "tags": meta.get("tags", []),
                "content_html": html_content,
            }
        )

    blogs.sort(key=lambda b: b["date"], reverse=True)
    return blogs


# --- Page builders ----------------------------------------------------------


def escape_html(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_blog_card_html(blog: dict) -> str:
    """Server-rendered markup for one blog card, matching the structure
    blogs.js builds client-side (renderCard), so Google (and anyone with
    JS disabled) sees real content and links on first load."""
    title = escape_html(blog["title"])
    return (
        f'<a href="/blogs/{blog["slug"]}/" class="blog-card">'
        f'<div class="blog-card-thumb"><img src="{escape_html(blog["thumbnail"])}" '
        f'alt="{title}" loading="lazy" /></div>'
        '<div class="blog-card-body">'
        f'<div class="blog-card-meta"><time>{escape_html(blog["formatted_date"])}</time>'
        f"<span>&bull;</span><span>{escape_html(blog['category'])}</span></div>"
        f"<h2>{title}</h2>"
        f'<p class="blog-card-desc">{escape_html(blog["description"])}</p>'
        "</div></a>"
    )


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
    PER_PAGE = 6
    first_page_html = "".join(render_blog_card_html(b) for b in blogs[:PER_PAGE])

    html = render_vars(
        html, {"blogs_json": blogs_json, "blog_cards_ssr": first_page_html}
    )

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
                "date_iso": iso_date(blog["date"]),
                "formatted_date": blog["formatted_date"],
                "category": blog["category"],
                "thumbnail": blog["thumbnail"],
                "image_width": blog["image_width"],
                "image_height": blog["image_height"],
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
