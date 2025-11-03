#!/usr/bin/env python3
"""
Ghost2Hugo v1.4.0 — Convert a Ghost CMS JSON backup to Hugo Markdown posts/pages.

Author: Daniel Bocksteger
Repository: https://github.com/regetskcob/Ghost2Hugo
License: MIT

✨ Features
------------
- Converts HTML → Markdown using html2text
- Generates Hugo-compatible YAML front matter
- Preserves SEO, author, cover, and image metadata
- Copies referenced images into each post's folder
- Rewrites all image URLs (content + front matter) to relative paths (./image.jpg)
- Validates and moves invalid outputs automatically
- Adds sensible Hugo defaults (description, cover, type, reading_time)
- Auto-selects OpenGraph image (og_image > feature_image > first content image)
- Cleans up emojis, umlauts, and all UTF-8 hex artifacts from slugs

🧠 Improvements in v1.4
------------------------
- 🧭 All image URLs are now rewritten to local relative paths (`./image.jpg`)
- 🔗 Front matter image fields (`featured_image`, `cover`, `seo.image`) are automatically localized
- 🪄 Added `rewrite_image_paths()` for consistent Markdown replacements
- 🧹 Minor console and code cleanup
"""

import os
import re
import json
import html2text
import shutil
import yaml
import argparse
from datetime import datetime
from urllib.parse import urlparse


# === Utility helpers ===

def normalize_umlauts(text: str) -> str:
    """Replace German umlauts and ß with ASCII equivalents."""
    replacements = {
        "ä": "ae", "ö": "oe", "ü": "ue",
        "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
        "ß": "ss",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def remove_emojis(s: str) -> str:
    """Remove all emojis and pictographic symbols, UCS-2 and UCS-4 safe."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002700-\U000027BF"  # dingbats
        "\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
        "\U00002600-\U000026FF"  # miscellaneous symbols
        "\U0001FA70-\U0001FAFF"  # extended pictographs
        "]+",
        flags=re.UNICODE,
    )
    # Also remove surrogate pairs (UCS-2 safe)
    s = re.sub(r"[\uD800-\uDBFF][\uDC00-\uDFFF]", "", s)
    return emoji_pattern.sub("", s)


def normalize_dashes(s: str) -> str:
    """Normalize unicode dashes to ASCII hyphen-minus."""
    return re.sub(r"[-–—‒−]", "-", s)


def strip_leading_hex_chains(s: str) -> str:
    """Remove Ghost’s UTF-8 hex-byte slugs like f0-9f-93-9a-..."""
    t = s.strip().lower()
    while True:
        m = re.match(r'^(?:[0-9a-f]{2}-){2,}[0-9a-f]{2}(?:-)?', t)
        if not m:
            break
        t = t[m.end():]
    return t.lstrip("-_").strip()


def clean_slug(slug_or_title: str) -> str:
    """Remove emojis and special symbols, normalize umlauts, and create a safe Hugo slug."""
    cleaned = remove_emojis(slug_or_title)
    cleaned = normalize_umlauts(cleaned)
    cleaned = re.sub(r"[^a-zA-Z0-9\-]+", "-", cleaned.lower())
    cleaned = re.sub(r"-+", "-", cleaned).strip("-")
    return cleaned


def safe_slug_from(post: dict) -> str:
    """Return a cleaned slug, prioritizing the TITLE over Ghost’s slug."""
    title = (post.get("title") or "").strip()
    ghost_slug = (post.get("slug") or "").strip()
    raw = normalize_dashes(title)
    raw = remove_emojis(raw)
    slug_from_title = clean_slug(raw)
    if slug_from_title:
        return slug_from_title
    ghost_raw = normalize_dashes(ghost_slug)
    ghost_raw = strip_leading_hex_chains(ghost_raw)
    ghost_raw = remove_emojis(ghost_raw)
    slug = clean_slug(ghost_raw)
    return slug or f"untitled-{post.get('id', 'noid')}"


def rewrite_image_paths(markdown: str) -> str:
    """Rewrite all Ghost image URLs to local relative paths (./filename)."""
    return re.sub(
        r'!\[(.*?)\]\((?:https?:\/\/[^)\/]+)?(?:\/content\/images\/[^\)]*\/)?([^\/\)]+\.(?:jpg|jpeg|png|gif|webp|avif))\)',
        r'![\1](./\2)',
        markdown,
        flags=re.IGNORECASE
    )


def ensure_image_alts(markdown: str, default_alt: str) -> str:
    """Fill empty Markdown image alts: ![](path) → ![default_alt](path)."""
    return re.sub(r'!\[\s*\]\(([^)]+)\)', fr'![{re.escape(default_alt)}](\1)', markdown)


def copy_images(markdown: str, images_dir: str, post_dir: str) -> (str, bool):
    """Copy referenced images into post directory; return (markdown, has_images)."""
    os.makedirs(post_dir, exist_ok=True)
    replaced = markdown
    found_images = False
    image_urls = re.findall(r"!\[.*?\]\((.*?)\)", markdown)

    for url in image_urls:
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        for root, _, files in os.walk(images_dir):
            if filename in files:
                src = os.path.join(root, filename)
                dest = os.path.join(post_dir, filename)
                shutil.copy2(src, dest)
                replaced = replaced.replace(url.strip(), f"./{filename}")
                found_images = True
                print(f"   📸 Copied image: {filename}")
                break
    return replaced.strip(), found_images


def validate_markdown(path: str) -> bool:
    """Check if a Markdown file contains valid YAML front matter."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if not content.strip().startswith("---"):
            return False
        parts = content.split("---")
        if len(parts) < 3:
            return False
        front = yaml.safe_load(parts[1])
        if not isinstance(front, dict):
            return False
        required = ["title", "slug"]
        if not all(k in front and front[k] for k in required):
            return False
        return True
    except Exception as e:
        print(f"⚠️  Validation error in {path}: {e}")
        return False


# === Core converter ===

def export_post(post, authors, images_dir, out_dir, invalid_dir, site_url, converter,
                count_valid, count_invalid, default_status=None):
    """Export a single post or page from Ghost to Hugo format."""

    title = (post.get("title") or "").strip()
    slug = safe_slug_from(post)
    date = post.get("published_at") or post.get("created_at")
    updated = post.get("updated_at")
    feature_image = post.get("feature_image")
    excerpt = (post.get("custom_excerpt") or "").strip()
    html_content = (post.get("html") or "").strip()
    tags = post.get("tags", [])
    author_id = post.get("published_by")
    author = authors.get(author_id, {})
    author_name = (author.get("name") or "Unknown").strip()
    author_bio = (author.get("bio") or "").strip()
    author_image = author.get("profile_image")
    reading_time = post.get("reading_time")
    meta_title = (post.get("meta_title") or "").strip()
    meta_description = (post.get("meta_description") or "").strip()
    og_image = post.get("og_image")
    post_type = post.get("type") or "post"

    html_content = html_content.replace("__GHOST_URL__", site_url)
    markdown_content = converter.handle(html_content).strip()
    title_plain = remove_emojis(title).strip()
    markdown_content = ensure_image_alts(markdown_content, title_plain or "image")
    markdown_content = rewrite_image_paths(markdown_content)

    if not excerpt:
        first_para = next((p.strip() for p in markdown_content.split("\n\n") if p.strip()), "")
        excerpt = (first_para[:157] + "…") if len(first_para) > 160 else first_para
    if not reading_time:
        words = len(re.findall(r"\w+", markdown_content))
        reading_time = max(1, round(words / 200))

    date_fmt = datetime.fromisoformat(date.replace("Z", "+00:00")).strftime("%Y-%m-%dT%H:%M:%S%z")
    lastmod_fmt = datetime.fromisoformat(updated.replace("Z", "+00:00")).strftime("%Y-%m-%dT%H:%M:%S%z") if updated else date_fmt
    is_draft = (default_status == "draft") if default_status else (post["status"] != "published")

    # === Front matter ===
    front_matter = {
        "title": title,
        "title_plain": title_plain or title,
        "date": date_fmt,
        "lastmod": lastmod_fmt,
        "slug": slug,
        "draft": is_draft,
        "type": post_type,
        "author": author_name,
        "reading_time": reading_time,
        "description": excerpt,
    }

    if author_bio:
        front_matter["author_bio"] = author_bio
    if author_image:
        front_matter["author_image"] = author_image.strip()

    # Localize feature image paths
    if feature_image:
        feat_name = os.path.basename(feature_image.strip())
        front_matter["featured_image"] = f"./{feat_name}"
        front_matter["cover"] = f"./{feat_name}"

    # --- SEO block ---
    seo_block = {}
    if meta_title:
        seo_block["title"] = meta_title
    if meta_description:
        seo_block["description"] = meta_description
    if og_image:
        og_name = os.path.basename(og_image.strip())
        seo_block["image"] = f"./{og_name}"
    elif feature_image:
        feat_name = os.path.basename(feature_image.strip())
        seo_block["image"] = f"./{feat_name}"
    else:
        match_first_image = re.search(r"!\[.*?\]\(([^)]+)\)", markdown_content)
        if match_first_image:
            seo_block["image"] = match_first_image.group(1).strip()
    if seo_block:
        front_matter["seo"] = seo_block

    # Tags
    if tags:
        tag_list = [t["name"].strip() if isinstance(t, dict) else str(t).strip() for t in tags if str(t).strip()]
        if tag_list:
            front_matter["tags"] = tag_list
            front_matter["categories"] = [tag_list[0]]

    yaml_front = yaml.safe_dump(front_matter, sort_keys=False, allow_unicode=True).strip()

    post_dir = os.path.join(out_dir, slug)
    markdown_replaced, has_images = copy_images(markdown_content, images_dir, post_dir)
    markdown_replaced = rewrite_image_paths(markdown_replaced)

    # Copy feature image to local bundle
    if feature_image:
        feature_filename = os.path.basename(feature_image.strip())
        for root, _, files in os.walk(images_dir):
            if feature_filename in files:
                shutil.copy2(os.path.join(root, feature_filename), os.path.join(post_dir, feature_filename))
                has_images = True
                print(f"   🌄 Feature image: {feature_filename}")
                break

    if has_images:
        markdown_path = os.path.join(post_dir, "index.md")
    else:
        shutil.rmtree(post_dir, ignore_errors=True)
        markdown_path = os.path.join(out_dir, f"{slug}.md")

    full_content = f"---\n{yaml_front}\n---\n\n{markdown_replaced}\n"
    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write(full_content.rstrip() + "\n")

    if not validate_markdown(markdown_path):
        count_invalid[0] += 1
        invalid_target = os.path.join(invalid_dir, slug)
        if has_images:
            shutil.move(os.path.dirname(markdown_path), invalid_target)
        else:
            shutil.move(markdown_path, invalid_target + ".md")
        print(f"⚠️  Invalid file moved to: {invalid_target}")
    else:
        count_valid[0] += 1
        imgs = "bundle" if has_images else "single"
        print(f"✅ [{post_type.upper()}] {slug} → {markdown_path}  ({imgs}, {reading_time} min read)")


# === Main CLI ===

def main():
    parser = argparse.ArgumentParser(description="Convert Ghost CMS JSON backup to Hugo Markdown files.")
    parser.add_argument("--input", required=True, help="Path to the Ghost JSON backup file")
    parser.add_argument("--images", required=True, help="Path to Ghost images directory")
    parser.add_argument("--output-posts", default="content/posts", help="Output folder for posts")
    parser.add_argument("--output-pages", default="content/pages", help="Output folder for pages")
    parser.add_argument("--output-invalid", default="content/invalid", help="Folder for invalid outputs")
    parser.add_argument("--site-url", default="https://example.com", help="Base URL for image and link rewriting")
    parser.add_argument("--default-status", choices=["published", "draft"], help="Override all post statuses (e.g., import everything as 'draft').")

    args = parser.parse_args()

    os.makedirs(args.output_posts, exist_ok=True)
    os.makedirs(args.output_pages, exist_ok=True)
    os.makedirs(args.output_invalid, exist_ok=True)

    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = False
    converter.body_width = 0

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "data" in data and "posts" in data["data"]:
        ghost_data = data["data"]
    elif "db" in data and isinstance(data["db"], list) and "data" in data["db"][0]:
        ghost_data = data["db"][0]["data"]
    else:
        raise ValueError("❌ Could not detect Ghost data structure")

    posts = ghost_data.get("posts", [])
    authors = {a["id"]: a for a in ghost_data.get("users", [])}

    count_valid = [0]
    count_invalid = [0]

    for post in posts:
        if post["status"] not in ["published", "draft"]:
            continue
        print(f"\n➡️  {post['title']} [{post['type']}]")
        target_dir = args.output_pages if post["type"] == "page" else args.output_posts
        export_post(post, authors, args.images, target_dir, args.output_invalid,
                    args.site_url, converter, count_valid, count_invalid, args.default_status)

    print("\n🎉 Conversion finished!")
    print(f"✅ Valid exports: {count_valid[0]}")
    print(f"⚠️ Invalid exports moved: {count_invalid[0]}")


if __name__ == "__main__":
    main()