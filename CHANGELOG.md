# 📜 Changelog

All notable changes to **Ghost2Hugo** are documented here.

---

## [v1.4.0] – 2025-11-03

### Added
- `rewrite_image_paths()` to normalize all image references (Markdown + front matter)
- Automatic path rewriting for `featured_image`, `cover`, and `seo.image`
- Local image path mapping (`./image.jpg`) compatible with Hugo bundles

### Fixed
- Broken absolute Ghost image URLs left in Markdown and front matter
- Inconsistent paths between copied files and Markdown references

### Changed
- Cleaner console output for post exports
- Updated inline comments for better readability

---

## [v1.3.0] – 2025-11-02

### Added
- `safe_slug_from()` with title-first fallback for robust slug generation
- `strip_leading_hex_chains()` to remove Ghost’s broken UTF-8 byte slugs
- Automatic unicode dash normalization for consistent filenames

### Fixed
- Hex-artifact slugs (e.g., `f0-9f-93-9a-das-geheime-leben-der-baeume`)
- UCS-2 / UCS-4 emoji removal inconsistencies on macOS and Windows
- Minor logging inconsistencies in export summary

### Changed
- Cleaner console output (`✅ [POST] slug → path`)
- Updated docstrings and inline comments for clarity
- Small code formatting cleanup (PEP 8 alignment)

---

## [v1.2] – 2025-11-01

### 🚀 Added
- 🧠 Automatic **OpenGraph image fallback** (`og_image → feature_image → first post image`)
- ✨ Automatic **reading_time** estimation (200 words per minute)
- 🪶 Auto-fills empty Markdown image alt-texts with the post title
- 🧩 New front matter fields: `title_plain`, `cover`, `type`, and `categories`

### 🛠️ Improved
- ⚙️ Better description fallback (uses first paragraph if `custom_excerpt` missing)
- 🔍 Validation now handles malformed front matter more gracefully
- ✅ Cleaner YAML output with normalized whitespace
- 📦 Improved folder structure for bundled posts with images

### 🧹 Internal
- Code cleanup and better logging output
- Prepared for publishing on GitHub (v1.2 release structure)

---

## [v1.0] – 2025-10-20

- Initial release of **Ghost2Hugo**
