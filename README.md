# Ghost2Hugo

A lightweight Python 3 tool to convert [Ghost CMS](https://ghost.org) JSON backups
into [Hugo](https://gohugo.io) compatible Markdown files.

## 🚀 Features
- Converts HTML → Markdown with `html2text`
- Generates Hugo YAML front matter
- Preserves SEO, tags, author info & images
- Validates output and moves invalid files automatically
- Works with Ghost v3–v6 backup formats

---

## 📦 Installation
```bash
git clone https://github.com/yourname/Ghost2Hugo.git
cd Ghost2Hugo
pip install -r requirements.txt
```

---

## 🧭 Usage
```bash
python3 ghost-to-hugo.py   --input ./data/ghost-backup.json   --images ./images   --output-posts ./content/posts   --output-pages ./content/pages   --output-invalid ./content/invalid   --site-url "https://example.com" --default-status "draft"
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

## ⚖️ License
Released under the [MIT License](LICENSE).
