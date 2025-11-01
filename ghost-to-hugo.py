#!/usr/bin/env python3

"""
Convert a Ghost CMS JSON backup to Hugo Markdown posts/pages.

Features:
- Converts HTML → Markdown using html2text
- Generates Hugo-compatible YAML front matter
- Preserves SEO, author, and image metadata
- Copies referenced images into each post's folder
- Validates output and moves invalid results to /invalid/
"""

import os
import re
import json
import html2text
import shutil
import unicodedata
import yaml
import argparse
from datetime import datetime
from urllib.parse import urlparse


# === Utility helpers ===

def yaml_safe(value: str) -> str:
    """Safely serialize strings for YAML front matter."""
    if value is None:
        return '""'
    dumped = yaml.safe_dump(value, allow_unicode=True)
    return dumped.strip()


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


def clean_slug(slug_or_title: str) -> str:
    """Remove emojis and special symbols, normalize umlauts, and create a safe slug."""
    # Remove all emojis and other non-BMP Unicode characters
    cleaned = re.sub(r"[\U00010000-\U0010FFFF]", "", slug_or_title)
    # Replace German umlauts and ß with ASCII equivalents
    cleaned = normalize_umlauts(cleaned)
    # Replace all non-alphanumeric characters with hyphens
    cleaned = re.sub(r"[^a-zA-Z0-9\-]+", "-", cleaned.lower())
    # Collapse multiple consecutive hyphens and trim edges
    cleaned = re.sub(r"-+", "-", cleaned).strip("-")
    return cleaned


def copy_images(markdown: str, images_dir: str, post_dir: str) -> (str, bool):
    """Copy referenced images into post directory; return (markdown, has_images)."""
    os.makedirs(post_dir, exist_ok=True)
    replaced = markdown
    found_images = False
    image_urls = re.findall(r"!\[.*?\]\((.*?)\)", markdown)

    for url in image_urls:
        parsed = urlparse(url)
        if "__GHOST_URL__" in url or "/content/images/" in url:
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
    raw_slug = (post.get("slug") or title).strip()
    slug = clean_slug(raw_slug or title)
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

    html_content = html_content.replace("__GHOST_URL__", site_url)
    markdown_content = converter.handle(html_content).strip()

    date_fmt = datetime.fromisoformat(date.replace("Z", "+00:00")).strftime("%Y-%m-%dT%H:%M:%S%z")
    lastmod_fmt = datetime.fromisoformat(updated.replace("Z", "+00:00")).strftime("%Y-%m-%dT%H:%M:%S%z") if updated else date_fmt
    
    is_draft = (
        default_status == "draft"
        if default_status
        else post["status"] != "published"
    )

    front_matter = {
        "title": title,
        "date": date_fmt,
        "lastmod": lastmod_fmt,
        "slug": slug,
        "draft": is_draft,
        "author": author_name,
    }

    if author_bio:
        front_matter["author_bio"] = author_bio
    if author_image:
        front_matter["author_image"] = author_image.strip()
    if excerpt:
        front_matter["description"] = excerpt
    if feature_image:
        front_matter["featured_image"] = f"./{os.path.basename(feature_image.strip())}"
    if reading_time:
        front_matter["reading_time"] = reading_time

    seo_block = {}
    if meta_title:
        seo_block["title"] = meta_title
    if meta_description:
        seo_block["description"] = meta_description
    if og_image:
        seo_block["image"] = f"./{os.path.basename(og_image.strip())}"
    if seo_block:
        front_matter["seo"] = seo_block

    if tags:
        front_matter["tags"] = [
            t["name"].strip() if isinstance(t, dict) else str(t).strip()
            for t in tags
        ]

    yaml_front = yaml.safe_dump(front_matter, sort_keys=False, allow_unicode=True).strip()
    full_content = f"---\n{yaml_front}\n---\n\n{markdown_content}\n"

    # === Copy images ===
    post_dir = os.path.join(out_dir, slug)
    markdown_with_local_images, has_images = copy_images(markdown_content, images_dir, post_dir)

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

    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write(full_content.rstrip() + "\n")

    # === Validate output ===
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
        print(f"✅ Exported: {markdown_path}")


# === Main CLI ===

def main():
    parser = argparse.ArgumentParser(
        description="Convert Ghost CMS JSON backup to Hugo Markdown files."
    )
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
        print(f"➡️  {post['title']} ({post['type']})")
        if post["type"] == "page":
            export_post(post, authors, args.images, args.output_pages, args.output_invalid, args.site_url,
                        converter, count_valid, count_invalid, args.default_status)
        elif post["type"] == "post":
            export_post(post, authors, args.images, args.output_posts, args.output_invalid, args.site_url,
                        converter, count_valid, count_invalid, args.default_status)
        else:
            print(f"⚠️  Unknown post type: {post['type']}")

    print("\n🎉 Conversion finished!")
    print(f"✅ Valid exports: {count_valid[0]}")
    print(f"⚠️ Invalid exports moved: {count_invalid[0]}")


if __name__ == "__main__":
    main()
