# LaTeX Templates Directory

This directory contains official LaTeX style files and templates for supported conferences.

## Directory Structure

```
templates/
├── neurips/          # NeurIPS conference templates
├── icml/             # ICML conference templates
├── acl/              # ACL conference templates
├── ieee/             # IEEE conference/journal templates
├── acm/              # ACM SIGCHI and other venues
├── arxiv/            # arXiv preprint templates (optional)
└── generic/          # Generic article templates
```

## How to Add Templates

### Option 1: Download Official Templates (Recommended)

**NeurIPS:**
```bash
cd templates/neurips/
# Download from: https://neurips.cc/Conferences/2025/PaperInformation/StyleFiles
wget https://media.neurips.cc/Conferences/NeurIPS2024/Styles/neurips_2024.zip
unzip neurips_2024.zip
```

**ICML:**
```bash
cd templates/icml/
# Download from: https://icml.cc/Conferences/2024/StyleAuthorInstructions
# Or use Overleaf template
```

**ACL:**
```bash
cd templates/acl/
# Clone from official repo
git clone https://github.com/acl-org/acl-style-files.git
mv acl-style-files/* .
```

**IEEE:**
```bash
cd templates/ieee/
# Download from: https://www.ieee.org/conferences/publishing/templates.html
# Or: https://www.ctan.org/pkg/ieeetran
```

**ACM:**
```bash
cd templates/acm/
# Download from: https://www.acm.org/publications/proceedings-template
# Get acmart class files
```

### Option 2: Use Overleaf Templates

All conferences provide Overleaf templates. You can:
1. Open Overleaf template for the conference
2. Download source files as ZIP
3. Extract to appropriate templates/ subdirectory

### Option 3: Install System-Wide (LaTeX Distribution)

Many style files are available in TeX Live or MiKTeX:
```bash
# TeX Live includes most styles
tlmgr install acmart ieeetran

# Then they're available system-wide (no need to copy)
```

## Required Files by Conference

### NeurIPS
```
templates/neurips/
├── neurips_2024.sty       # Required: Main style file
├── neurips_2025.sty       # Or current year
├── template.tex           # Optional: Example document
└── example.bib            # Optional: Example bibliography
```

### ICML
```
templates/icml/
├── icml2024.sty           # Required: Main style file
├── fancyhdr.sty           # Required: Header/footer (included)
├── template.tex           # Optional: Example
└── example.bib            # Optional
```

### ACL
```
templates/acl/
├── acl.sty                # Required: Main style file
├── acl_natbib.bst         # Required: Bibliography style
└── template.tex           # Optional
```

### IEEE
```
templates/ieee/
├── IEEEtran.cls           # Required: Document class
├── IEEEtran.bst           # Required: Bibliography style
└── bare_conf.tex          # Optional: Conference template
```

### ACM
```
templates/acm/
├── acmart.cls             # Required: Document class
├── ACM-Reference-Format.bst  # Required: Bibliography
└── sample-sigconf.tex     # Optional: Example
```

## Template Usage in Bundle

Templates are accessed by agents via the `@research:templates/` namespace:

```python
# Example: In venue-formatter agent
# Copy NeurIPS template to user directory
bash("cp @research:templates/neurips/* ./")
```

Or via Python scripts:

```python
# scripts/compile_latex.py
bundle_root = Path(os.getenv('AMPLIFIER_BUNDLE_ROOT', Path(__file__).parent.parent))
template_dir = bundle_root / 'templates' / format_name

# Copy style files to user's directory
for style_file in template_dir.glob('*.sty'):
    shutil.copy(style_file, user_dir)
```

## License Considerations

### ⚠️ Check Before Redistribution

Conference style files have different licenses:

| Conference | License | Can Bundle? |
|------------|---------|-------------|
| **NeurIPS** | LaTeX Project Public License (LPPL) | ✅ Yes |
| **ICML** | Public domain / permissive | ✅ Yes |
| **ACL** | Apache 2.0 (GitHub repo) | ✅ Yes (with attribution) |
| **IEEE** | LPPL 1.3 | ✅ Yes |
| **ACM** | ACM copyright (acmart) | ⚠️ Check terms |

**Recommendation:** 
- Include permissively-licensed templates
- Document download links for others
- Always attribute original sources

## Alternative: Download Scripts

Instead of bundling templates, you can provide download automation:

```bash
# templates/download.sh
#!/bin/bash

echo "Downloading NeurIPS templates..."
curl -L https://media.neurips.cc/Conferences/NeurIPS2024/Styles/neurips_2024.zip -o neurips.zip
unzip -d neurips/ neurips.zip

echo "Cloning ACL templates..."
git clone https://github.com/acl-org/acl-style-files.git acl/

# etc.
```

## Current Status

**As of initial bundle creation:**
- ✅ Directory structure created
- ⚠️ No template files included yet
- ✅ Scripts reference template paths
- ✅ Agents know how to use templates

**To make templates functional:**
1. Download official style files (see Option 1 above)
2. Place in appropriate subdirectories
3. Test compilation with `scripts/compile_latex.py`

## Testing Without Templates

You can test the bundle WITHOUT templates by:
1. Using system-wide LaTeX packages (if installed via TeX Live)
2. Creating minimal test documents that don't require conference styles
3. Testing agent delegation and workflow (not compilation)

## Help

For detailed formatting requirements, see:
- `references/latex-style-guides/INDEX.md` - Complete guide index
- `references/latex-style-guides/neurips-style-guide.md` - Example comprehensive guide
- Conference-specific guides in same directory

For quick conference specifications (agent-facing), see:
- `context/conference-formats/*.md` - Concise specs used by agents

---

**Last Updated:** 2026-02-04  
**Status:** Templates directory ready, awaiting style file downloads
