# noufal.me

Personal portfolio and blog. Plain HTML, CSS, and JS — built with a small
Python static site generator. No framework, no build chain beyond
`build/build.py`.

Live at [noufal.me](https://noufal.me).

## Stack

- **Content:** Markdown files with frontmatter (`content/blogs/`)
- **Templates:** Plain HTML with a tiny `{{ include:file.html }}` /
  `{{ variable }}` substitution system (`templates/`)
- **Styling:** Plain CSS, dark-only, Geist font (`static/css/style.css`)
- **Search & filtering** on the blogs page: vanilla JS, no framework
  (`static/js/blogs.js`)
- **Build:** `build/build.py` — parses Markdown, renders templates,
  outputs static HTML to `dist/`
- **Dependency management:** [uv](https://docs.astral.sh/uv/)

## Project structure

```
noufal-me/
├── build/
│   └── build.py            # the static site generator
├── content/
│   └── blogs/               # blog posts as Markdown + frontmatter
├── static/
│   ├── css/style.css
│   ├── js/                  # blogs.js (search/filter/pagination), main.js
│   ├── images/               # profile.webp, icon.png
│   └── blog-thumbnails/      # one thumbnail per blog post
├── templates/
│   ├── index.html            # home page
│   ├── blogs_index.html      # blog listing page
│   ├── blog_detail.html      # single blog post page
│   └── _footer.html          # shared footer partial
├── dev.sh                    # rebuild + serve locally
├── pyproject.toml / uv.lock  # dependencies (markdown)
└── dist/                     # build output (gitignored, not committed)
```

## Adding a new blog post

1. Add a Markdown file to `content/blogs/your-slug.md` with frontmatter:

   ```markdown
   ---
   title: Your Post Title
   date: "2026-01-15"
   description: A short description shown on the blog card.
   author: Mohammed Noufal
   thumbnail: /blog-thumbnails/your-slug.webp
   category: Thoughts
   tags:
     - tag-one
     - tag-two
   ---

   Your post content in Markdown...
   ```

2. Add a matching thumbnail to `static/blog-thumbnails/your-slug.webp`.
3. Run the build (see below). The post is picked up automatically —
   no other file needs editing.

## Local development

```bash
./dev.sh          # build + serve at http://localhost:3000
./dev.sh 8080      # serve on a custom port
```

`dev.sh` does three things on every run:

1. Kills any server already running on that port
2. Runs `uv run build/build.py` to rebuild `dist/`
3. Serves `dist/` with `python3 -m http.server`

Since `dist/` is fully regenerated each time, **there's no watch mode** —
after editing a template, style, or blog post, just re-run `./dev.sh`
(or `Ctrl+C` and run it again) to see the change.

## Building manually

```bash
uv run build/build.py
```

Output goes to `dist/`:

- `dist/index.html`
- `dist/blogs/index.html`
- `dist/blogs/<slug>/index.html` — one per post
- `dist/static/...` — copied as-is

## Deployment

Hosted on **Cloudflare Pages**, connected directly to this repo.
Every push to `main` triggers an automatic build and deploy.

- **Build command:** `python3 build/build.py`
- **Build output directory:** `dist`

Cloudflare's build step also runs `pip install .` before the build
command, which is why `pyproject.toml` sets `[tool.setuptools]
py-modules = []` — without it, setuptools tries (and fails) to treat
`static/`, `content/`, and `templates/` as installable Python packages.
