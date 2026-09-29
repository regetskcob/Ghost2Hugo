# 🪄 Ghost2Hugo

Convert your **Ghost CMS JSON backup** into a fully structured, **Hugo-compatible Markdown** blog — including metadata, images, and SEO fields.

---

## ✨ Features

- 🧩 Converts Ghost **HTML → Markdown** using `html2text`
- 🪶 Generates valid **YAML front matter** for Hugo
- 📸 Copies referenced images into the correct post folders and rewrites references in markdown content and front-matter params
- 🔍 Adds **SEO metadata**, including automatic OpenGraph image detection
- 🧠 Calculates `reading_time` automatically (200 WPM)
- 🗂️ Adds `cover`, `categories`, and `title_plain` for Hugo theme compatibility
- 🧾 Validates output and moves invalid files automatically
- ⚙️ Supports pages and posts separately
- 🏷️ Normalizes umlauts, removes emojis, and ensures safe slugs
- 🪄 Optional `--default-status` to import everything as draft or published
- ✏️ Cleans up emojis, umlauts, and **Ghost’s UTF-8 hex slugs** (like `f0-9f-93-9a-*`)


#### 🧾 About Validation and “Invalid” Files

Ghost2Hugo automatically validates each generated Markdown file to ensure that it can be processed correctly by Hugo.  
A file is considered **invalid** if any of the following conditions apply:

- 🧩 **Missing or malformed front matter:**  
  The file does not start with a proper YAML front matter block delimited by `---` lines.  
- ⚠️ **Invalid YAML structure:**  
  The YAML section cannot be parsed (for example due to unescaped quotes or special characters).  
- 🚫 **Missing required metadata:**  
  The fields `title` and `slug` are mandatory — if either is missing or empty, the file is marked invalid.  
- 🪶 **Corrupted formatting:**  
  If indentation or line breaks inside the YAML front matter cause parsing errors.

When a file fails validation, Ghost2Hugo **moves it automatically** to the `content/invalid/` directory:

- If the post includes images, the **entire post folder** (with its images) is moved.  
- If it’s a standalone Markdown file, only the `.md` file is moved.

This ensures that Hugo never breaks on bad input, and you can manually inspect or fix those files later.

---

## 📦 Installation
You can decide between two options to get the script. 

1. Clone this repo:
```bash
git clone https://github.com/regetskcob/Ghost2Hugo.git
cd Ghost2Hugo
pip install -r requirements.txt
```
2. download the script from the repository-releases.

---

## 🧮 CLI Options

| Flag | Description |
|------|--------------|
| `--input` | Path to Ghost JSON export |
| `--images` | Path to Ghost images folder |
| `--output-posts` | Output directory for posts |
| `--output-pages` | Output directory for pages |
| `--output-invalid` | Directory for invalid results |
| `--site-url` | Base URL for image and link rewriting |
| `--default-status` | Force all posts to be `"draft"` or `"published"` |

---

## 🧭 Usage
```bash
python3 ghost-to-hugo.py \
  --input "./backup/data/fotografie-technologie.ghost.2025-10-11-12-12-44.json" \
  --images "./backup/images" \
  --output-posts "./ghost2hugo/content/posts" \
  --output-pages "./ghost2hugo/content/pages" \
  --output-invalid "./ghost2hugo/content/invalid" \
  --site-url "https://regetskcob.github.io" \
  --default-status "draft"
```

> 🧠 Tip: Use `--default-status "draft"` for reviewing converted content before publishing.

### Example Output
Each Ghost post becomes a Hugo Markdown bundle:

```
content/posts/wander-dir-den-kopf-frei/
├── index.md
├── dscf2292.jpg
└── dscf1835.jpg
```

With front matter like:

```yaml
---
title: "📸 + 🥾 | Wander dir den Kopf frei!"
title_plain: "Wander dir den Kopf frei!"
date: 2020-06-13T13:52:53+0000
lastmod: 2024-11-17T15:06:44+0000
slug: wander-dir-den-kopf-frei-wanderbericht-ausm-uedemer-hochwald
draft: true
type: post
author: Daniel Bocksteger
reading_time: 7
description: "Ein Wochenendausflug in den Uedemer Hochwald – Ruhe, Natur und Bewegung vor der Haustür."
tags:
- Wandern
- Natur
- Fotografie
categories:
- Wandern
featured_image: ./dscf2292.jpg
cover: ./dscf2292.jpg
seo:
  title: "Wander dir den Kopf frei!"
  description: "Ein Wochenendausflug in den Uedemer Hochwald – Ruhe, Natur und Bewegung vor der Haustür."
  image: ./dscf2292.jpg
---
```

---

## 🚧 Known Issues & Roadmap

Open points from a code review (v1.4.0). They are not fixed yet — contributions welcome.

### Metadata from related Ghost tables
- [ ] **Tags** are stored in `tags` + `posts_tags`, not on the post itself → `tags`/`categories` are currently empty for real exports.
- [ ] **SEO fields** (`meta_title`, `meta_description`, `og_image`) live in `posts_meta` since Ghost 4 → the `seo` block is mostly empty.
- [ ] **Authors** are linked via `posts_authors`; `published_by` is missing or wrong in newer Ghost versions → author may be `Unknown`.
- [ ] Filter out Ghost's internal tags (`#hash-tags`, `visibility: internal`).

### Bugs
- [ ] `ensure_image_alts()` uses `re.escape()` in the replacement → empty alt texts become `Wander\ dir\ den\ Kopf\ frei!`.
- [ ] `remove_emojis()` misses variation selectors (U+FE0F), ZWJ sequences, `⭐` (U+2B50) and similar; the surrogate regex has no effect in Python 3. `title_plain` also keeps separators such as `+` and `|` (e.g. `+  | Wander dir den Kopf frei!`).
- [ ] Slugs drop accented characters (`Café in Málaga` → `caf-in-m-laga`); use `unicodedata` NFKD normalization.
- [ ] `featured_image`/`cover`/`seo.image` are always set to `./<basename>`, even if the file wasn't copied (e.g. external Unsplash URLs → `./photo-123?w=2000`).
- [ ] `og_image` is referenced in `seo.image` but never copied into the bundle.
- [ ] `author_image` keeps the `__GHOST_URL__` placeholder (only `html` gets replaced).
- [ ] Image lookup by basename via `os.walk` takes the first match → may copy a resized variant from `images/size/w600/…` or a same-named image from another year.
- [ ] Files and media (`/content/files/`, `/content/media/`) and linked full-size images (`[![](img)](full.jpg)`) are not copied or rewritten.
- [ ] Missing keys crash the run (`post["status"]`, `post["type"]`, `post["title"]`, missing dates).

### Migration / SEO
- [ ] Slugs are generated from the title instead of Ghost's slug → old URLs break. Add `aliases:` with the old Ghost path or prefer the Ghost slug when it isn't a hex artifact.
- [ ] Duplicate slugs (same title) silently overwrite each other.
- [ ] Internal links stay absolute to old Ghost URLs; `--site-url` defaults to `https://example.com`.
- [ ] `description` fallback uses the first Markdown paragraph and can contain Markdown syntax (images, headings); consider Ghost's `plaintext` field.
- [ ] Ghost cards (embeds/iframes, bookmarks, galleries) are dropped or flattened by `html2text`.
- [ ] `type: post` may conflict with themes expecting `posts` or a section-derived type.
- [ ] Posts with status `scheduled` or `sent` (newsletter-only) are skipped without notice.

### Robustness & performance
- [ ] Re-runs: `shutil.move` into existing `invalid/` targets nests or fails; stale `slug.md` / `slug/` outputs remain.
- [ ] Validation is weak: `yaml.safe_dump` always produces valid YAML, and `split("---")` breaks if `---` appears in the front matter.
- [ ] `os.walk` over the full image directory for every image of every post → build a filename index once.

### Code quality
- [ ] Add tests (pytest) for slug, emoji and image-path helpers.
- [ ] `rewrite_image_paths()` is applied twice; `copy_images()` then replaces already rewritten paths.
- [ ] Replace list-based counters (`count_valid[0]`) with return values.
- [ ] Pin versions in `requirements.txt`.

---

## 🧰 Requirements
- Python 3.9+
- `html2text`
- `PyYAML`

---

## 🧑‍💻 Author
**Daniel Bocksteger**  
Software Engineer & Photographer  
https://regetskcob.github.io

---

## 🫵 Contribution
I'd be really happy in case my script serves a benefit to you. If you encounter a problem with you backup (e.g. with a newer Ghost version) or have another feature request, please consider writing an Issue or submitting a pull request.

---

## ⚖️ License
Released under the [MIT License](LICENSE).
