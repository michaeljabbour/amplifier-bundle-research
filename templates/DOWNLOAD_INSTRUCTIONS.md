# Template Download Instructions

## Automated Download (Recommended)

Use the provided script to download most templates automatically:

```bash
# Download all available templates
python scripts/download_templates.py --all

# Download specific conference
python scripts/download_templates.py --conference neurips
```

---

## Download Status

### ✅ Automated Downloads Working

**ACL** - Git clone from official repository
```bash
python scripts/download_templates.py --conference acl
# Downloads from: https://github.com/acl-org/acl-style-files
```

**IEEE** - CTAN download
```bash
python scripts/download_templates.py --conference ieee
# Downloads from: https://mirrors.ctan.org/macros/latex/contrib/IEEEtran.zip
```

### ⚠️ Manual Download Required

**NeurIPS** - Media server requires browser access
```bash
# Option 1: Direct download
# Visit: https://neurips.cc/Conferences/2024/PaperInformation/StyleFiles
# Download neurips_2024.zip
# Extract to: templates/neurips/

# Option 2: Overleaf
# Visit: https://www.overleaf.com/latex/templates/neurips-2024/tpsbbrdqcmsh
# Download source as ZIP
# Extract neurips_2024.sty to: templates/neurips/

# Option 3: GitHub
git clone https://github.com/goodfeli/nips_2016.git
cp nips_2016/neurips_*.sty templates/neurips/
```

**ICML** - Conference website
```bash
# Visit: https://icml.cc/Conferences/2024/StyleAuthorInstructions
# Download the LaTeX style package
# Extract icml2024.sty to: templates/icml/

# Alternative: Overleaf
# Visit: https://www.overleaf.com/latex/templates/icml-2024/
# Download and extract to: templates/icml/
```

**ACM** - ACM website requires authentication
```bash
# Option 1: Direct download
# Visit: https://www.acm.org/publications/proceedings-template
# Click "LaTeX (Version 2.10)" download
# Extract to: templates/acm/

# Option 2: CTAN
wget https://mirrors.ctan.org/macros/latex/contrib/acmart.zip
unzip acmart.zip -d templates/acm/

# Option 3: Overleaf
# Visit: https://www.overleaf.com/latex/templates/acm-conference-proceedings-primary-article-template/
# Download source and extract to: templates/acm/
```

---

## Required Files by Conference

### NeurIPS
```
templates/neurips/
├── neurips_2024.sty       ✅ REQUIRED
└── neurips_2025.sty       (or current year)
```

### ICML
```
templates/icml/
├── icml2024.sty           ✅ REQUIRED
└── fancyhdr.sty           (usually included)
```

### ACL
```
templates/acl/
├── acl.sty                ✅ REQUIRED (downloaded ✅)
└── acl_natbib.bst         ✅ REQUIRED (downloaded ✅)
```

### IEEE
```
templates/ieee/
├── IEEEtran.cls           ✅ REQUIRED (downloaded ✅)
└── IEEEtran.bst           ✅ REQUIRED (downloaded ✅)
```

### ACM
```
templates/acm/
├── acmart.cls             ✅ REQUIRED
├── ACM-Reference-Format.bst  ✅ REQUIRED
└── sample-sigconf.tex     (optional example)
```

---

## Verification

After downloading, verify templates are present:

```bash
# Check all templates
ls templates/*/

# Verify required files
ls templates/neurips/neurips_2024.sty
ls templates/icml/icml2024.sty
ls templates/acl/acl.sty
ls templates/ieee/IEEEtran.cls
ls templates/acm/acmart.cls
```

---

## Alternative: System-Wide LaTeX Packages

If you have TeX Live installed, many styles are available system-wide:

```bash
# Check if already installed
kpsewhich IEEEtran.cls
kpsewhich acmart.cls

# Install via TeX Live Manager
tlmgr install ieeetran acmart

# No need to download if system-wide packages are available
```

---

## Troubleshooting

### "File not found" errors during compilation

**Cause:** Style file not in templates/ or LaTeX path

**Fix:**
1. Verify file exists: `ls templates/neurips/neurips_2024.sty`
2. Check compilation script copied it: `ls ./neurips_2024.sty` (in paper directory)
3. Or install system-wide via `tlmgr`

### Download script shows "403 Forbidden"

**Cause:** Conference website protects direct downloads

**Fix:** Use manual download instructions above

### "git: command not found" for ACL

**Cause:** Git not installed

**Fix:**
```bash
# Install git, then retry
brew install git  # macOS
# OR manually download:
# Visit: https://github.com/acl-org/acl-style-files
# Download ZIP and extract to templates/acl/
```

---

## Quick Start

**Fastest path to working templates:**

```bash
# 1. Download IEEE and ACL (automated)
python scripts/download_templates.py --all

# 2. Download NeurIPS manually (most common conference)
# Visit: https://www.overleaf.com/latex/templates/neurips-2024/tpsbbrdqcmsh
# Download, extract neurips_2024.sty to templates/neurips/

# 3. Test compilation
python scripts/compile_latex.py --help
```

---

**Last Updated:** 2026-02-04  
**Script:** `scripts/download_templates.py` automates most downloads  
**Status:** ACL ✅ IEEE ✅ | NeurIPS ⚠️ ICML ⚠️ ACM ⚠️ (manual required)
