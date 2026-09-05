# Agentic AI notebook

A five-module study companion for Andrew Ng's Agentic AI course. Each chapter pairs explanations with worked examples, C4-style diagrams, runnable Python practice, and recall questions.

- [Course library](index.html)
- [Module 1: Foundations](chapters/module-1.html)
- [Module 2: Reflection](chapters/module-2.html)
- [Module 3: Tool use](chapters/module-3.html)
- [Module 4: Evaluation](chapters/module-4.html)
- [Module 5: Planning and teams](chapters/module-5.html)

## Read locally

From this repository:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/`. No build dependencies or remote fonts are required. Learning checklists are stored only in the current browser. Reading and code downloads work without JavaScript; interactive comparisons, trace controls, clipboard buttons, and checklist persistence need JavaScript.

## Edit and build

Chapter bodies live in `notes/module-*.html`. Edit these source fragments, then regenerate the public pages:

```sh
python3 scripts/build_site.py
python3 scripts/check_site.py
```

The builder uses only the Python standard library. Page titles and index summaries live in `scripts/build_site.py`; shared presentation and behavior live in `styles.css` and `app.js`. Do not edit generated chapter pages directly.

## Practice

The `labs/` exercises use the Python standard library and deterministic fixtures. They make no model or external-service calls. Run any file with Python 3, for example:

```sh
python3 labs/module_3_tools.py
```

The original `.ipynb` course labs remain available as source material. They depend on helper modules, data, and services not all included in this checkout; the new exercises do not claim to reproduce those environments or benchmark LLM quality.

## Source and archive

The learner PDFs and original notebooks are the course sources. Chapters distinguish course material from explanatory engineering additions. C4 conventions follow [system context](https://c4model.com/diagrams/system-context) and [component diagrams](https://c4model.com/diagrams/component).

The previous HTML/CSS edition and its referenced images are preserved under `archive/2026-09-05/`. Its attribution and license disclosure remain in its index. The approved prototype URL, `preview/`, redirects to the new Module 1. The active site retains the original root/index and chapter URLs for GitHub Pages compatibility.
