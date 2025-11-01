# 📜 Changelog

All notable changes to **Ghost2Hugo** are documented here.

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
- Converted Ghost HTML → Markdown
- Supported image copying and basic front matter
