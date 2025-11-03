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
git clone https://github.com/yourname/Ghost2Hugo.git
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
python3 ghost-to-hugo.py
  --input "./backup/data/fotografie-technologie.ghost.2025-10-11-12-12-44.json"
  --images "./backup/images"
  --output-posts "./ghost2hugo/content/posts"
  --output-pages "./ghost2hugo/content/pages"
  --output-invalid "./ghost2hugo/content/invalid"
  --site-url "https://regetskcob.github.io"
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
tags: ["Wandern", "Natur", "Fotografie"]
categories: ["Wandern"]
featured_image: ./dscf2292.jpg
cover: ./dscf2292.jpg
seo:
  title: "Wander dir den Kopf frei!"
  description: "Ein Wochenendausflug in den Uedemer Hochwald – Ruhe, Natur und Bewegung vor der Haustür."
  image: ./dscf2292.jpg
---
```

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
