# Ghost2Hugo

A lightweight Python 3 tool to convert [Ghost CMS](https://ghost.org) JSON backups
into [Hugo](https://gohugo.io) compatible Markdown files.

## 🚀 Features
- Converts HTML → Markdown with `html2text`
- Generates Hugo YAML front matter
- Preserves SEO, tags, author info & images
- Validates output and moves invalid files automatically
- Works with Ghost v3–v6 backup formats

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

### Example Output
```
➡️  About Me (page)
✅ Exported: content/pages/about-me.md
➡️  Outside Project – Freedom & Adventure (post)
✅ Exported: content/posts/outside-project-freedom-adventure/index.md

🎉 Conversion finished!
✅ Valid exports: 80
⚠️ Invalid exports moved: 0
```

---

## 🧰 Requirements
- Python 3.8+
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
