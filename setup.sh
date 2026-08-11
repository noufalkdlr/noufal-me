#!/usr/bin/env bash
# Scaffolds the noufal-me-static project folder structure.
# Creates empty directories with .gitkeep so git tracks them.

set -e

ROOT="$(dirname "$(readlink -f "$0")")"
cd "$ROOT"

# Folders that should exist but stay empty (images go here manually) -> .gitkeep
empty_dirs=(
	"static/images"
	"static/blog-thumbnails"
)

# Blank (non-image) files to create, grouped by their folder
files=(
	"content/blogs/how-i-became-an-arch-linux-user.md"
	"content/blogs/why-freelancers-need-to-help-each-other.md"
	"static/css/style.css"
	"static/js/main.js"
	"templates/base.html"
	"templates/_footer.html"
	"templates/index.html"
	"templates/blogs_index.html"
	"templates/blog_detail.html"
	"build/build.py"
)

for dir in "${empty_dirs[@]}"; do
	mkdir -p "$dir"
	touch "$dir/.gitkeep"
	echo "created: $dir/.gitkeep"
done

for file in "${files[@]}"; do
	mkdir -p "$(dirname "$file")"
	touch "$file"
	echo "created: $file"
done

mkdir -p dist
echo "created: dist/"

echo "Done. Folder structure ready."
