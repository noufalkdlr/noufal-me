"""
build.py — Static site build script.

Run from the project root:
    python build/build.py

Output goes to dist/:
    dist/index.html
    dist/static/...

Currently just copies the home page and static assets as-is.
Once more pages (blogs) are added, this will grow to render
templates with Jinja2 + Markdown instead of a plain copy.
"""

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
DIST = ROOT / "dist"

INCLUDE_PATTERN = re.compile(r"\{\{\s*include:([\w.\-]+)\s*\}\}")


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


def copy_home_page() -> None:
    src = TEMPLATES / "index.html"
    dst = DIST / "index.html"
    html = src.read_text(encoding="utf-8")
    html = render_includes(html)
    dst.write_text(html, encoding="utf-8")


def main() -> None:
    clean_dist()
    copy_static()
    copy_home_page()
    print(f"Build complete → {DIST}")


if __name__ == "__main__":
    main()