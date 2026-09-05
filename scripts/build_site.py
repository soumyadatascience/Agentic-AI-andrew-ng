"""Build the static notebook from notes/*.html. Python standard library only."""
from pathlib import Path
from html import escape
import re

ROOT = Path(__file__).resolve().parents[1]
MODULES = [
    ("Foundations", "Introduction to agentic workflows", "From a prompt<br>to a working workflow.", "A model generates an answer. A workflow organizes the work around it: gathering information, taking actions, checking results, and deciding what comes next.", "Decompose a task, explain who executes each step, and trace a small workflow through a human-review decision.", "workflow"),
    ("Reflection", "The reflection design pattern", "Give the draft<br>a useful second pass.", "Generate a candidate, inspect real evidence, and revise. Then measure whether the extra work improved the result.", "Build a draft–review–revise loop, diagnose a SQL error, and evaluate the value of reflection.", "reflection"),
    ("Tool use", "Functions, schemas, and execution", "Let the model ask.<br>Let your code act.", "Follow a tool request from its schema to an executed function—and carry the observed result into the next model turn.", "Build a manual dispatcher, preserve tool-call history, and handle failures and termination explicitly.", "tools"),
    ("Evaluation", "Practical development and error analysis", "Find the failure.<br>Choose the next fix.", "Turn outputs and traces into evidence. Measure the weak component, change it deliberately, and check the whole workflow again.", "Write an evaluation, diagnose overlapping failures, and defend a measured improvement.", "evaluation"),
    ("Planning & teams", "Patterns for greater autonomy", "Plan the work.<br>Keep control explicit.", "Treat plans as proposals, make state changes inspectable, and coordinate specialized roles through concrete handoffs.", "Explain planning boundaries, test state changes and retries, and distinguish fixed pipelines from planner-managed teams.", "planning"),
]


def head(title, prefix="../"):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Agentic AI study notes with concrete examples, C4 diagrams, code, and runnable practice."><title>{escape(title)} · AI engineering notebook</title><link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Crect width='40' height='40' rx='10' fill='%23173e32'/%3E%3Ctext x='20' y='28' text-anchor='middle' fill='%23dcf492' font-size='28' font-family='Georgia'%3Ea%3C/text%3E%3C/svg%3E"><link rel="stylesheet" href="{prefix}styles.css"><script src="{prefix}app.js" defer></script></head>'''


def header(prefix="../", library=False):
    return f'''<a class="skip-link" href="#main">Skip to the notes</a><header class="topbar"><a class="notebook-brand" href="{prefix}index.html"><span class="brand-symbol" aria-hidden="true">a.</span> AI engineering <span class="brand-subtitle">/ notebook</span></a><div class="topbar-right"><a href="{prefix}{'chapters/module-1.html' if library else 'index.html'}">{'Start reading →' if library else 'Course library ↗'}</a><span class="edition">Andrew Ng · Agentic AI</span></div><div class="reading-progress" aria-hidden="true"></div></header>'''


def build():
    for n, (name, subtitle, title, intro, outcome, lab) in enumerate(MODULES, 1):
        content = (ROOT / f"notes/module-{n}.html").read_text()
        sections = re.findall(r'<section\b[^>]*id="([^"]+)"[^>]*data-nav="([^"]+)"', content)
        if not sections:
            # HTML attribute order need not put id before data-nav.
            for tag in re.findall(r'<section\b[^>]*>', content):
                nav = re.search(r'data-nav="([^"]+)"', tag)
                ident = re.search(r'id="([^"]+)"', tag)
                if nav and ident: sections.append((ident[1], nav[1]))
        assert len(sections) >= 6, f"Module {n}: missing chapter sections"
        toc = ''.join(f'<a href="#{ident}"><span>{i:02}</span> {label}</a>' for i, (ident, label) in enumerate(sections, 1))
        mobile = ''.join(f'<a href="#{ident}">{i:02} · {label}</a>' for i, (ident, label) in enumerate(sections, 1))
        counter = 0
        def add_kicker(match):
            nonlocal counter
            counter += 1
            return match[0] + f'<p class="section-kicker">{counter:02} / {sections[counter-1][1]}</p>'
        # Module 1 already has its approved kicker text.
        if n != 1:
            content = re.sub(r'<section class="lesson"[^>]*>', add_kicker, content)
        prev = f'<a href="module-{n-1}.html"><span>Previous module</span>← {MODULES[n-2][0]}</a>' if n > 1 else '<a href="../index.html"><span>Course library</span>All five modules</a>'
        next_link = f'<a href="module-{n+1}.html"><span>Next module</span>{MODULES[n][0]} →</a>' if n < 5 else '<a href="../index.html"><span>Return to your learning path</span>Course library →</a>'
        html = head(f"{n:02} · {name}") + f'<body data-module="{n}">' + header() + f'''<details class="mobile-toc"><summary>In this chapter · {name}</summary><nav aria-label="Mobile chapter navigation">{mobile}</nav></details><div class="layout"><aside class="sidebar"><p class="side-caption">Module {n:02} / 05</p><p class="course-name">{name}</p><nav class="toc" aria-label="Chapter sections">{toc}</nav><div class="side-bottom"><p class="side-caption">Read · trace · build</p><p>{outcome}</p><a href="../labs/module_{n}_{lab}.py" download>↓ Python practice file</a><a href="#sources">Sources & teaching notes</a></div></aside><main class="reading" id="main"><header class="chapter-intro"><p class="crumb">Agentic AI <span>/</span> Module {n:02} <span>/</span> {name}</p><p class="eyebrow">{subtitle}</p><h1>{title}</h1><p class="intro-text">{intro}</p><div class="chapter-meta"><span>{n:02} / 05 modules</span><span>Concepts + worked examples + practice</span><span>Python basics helpful</span></div><div class="outcome"><span class="arrow" aria-hidden="true">↳</span><p><strong>By the end of this chapter</strong>{outcome}</p></div></header>{content}<footer class="end-note">{prev}{next_link}</footer></main></div></body></html>'''
        (ROOT / f"chapters/module-{n}.html").write_text(html)

    rows = ''
    for n, (name, subtitle, title, intro, outcome, lab) in enumerate(MODULES, 1):
        rows += f'''<article class="library-row" id="module-{n}"><div class="library-number">{n:02}</div><div class="library-copy"><p class="panel-label">{subtitle}</p><h2><a href="chapters/module-{n}.html">{name}<span aria-hidden="true">↗</span></a></h2><p>{outcome}</p><div class="library-row-meta"><span>C4 diagrams</span><a href="labs/module_{n}_{lab}.py" download>Python exercise ↓</a><span data-course-progress="{n}">4 learning checks</span></div></div></article>'''
    html = head("Agentic AI · Course library", "") + '<body data-page="library">' + header('', True) + f'''<main class="library" id="main"><header class="library-intro"><div><p class="eyebrow">Your learning path</p><h1>Agentic AI.<br><em>From foundations to practice.</em></h1><p>Understand the mechanism. Follow a real example. Build the small version yourself.</p></div><aside class="library-note"><span class="panel-label">The approach</span><ol><li>Read the idea.</li><li>Trace the boundaries.</li><li>Run the code.</li><li>Explain it without looking.</li></ol><span class="subtle">Five modules · five runnable exercises</span></aside></header><section aria-labelledby="library-title"><div class="library-section-head"><h2 id="library-title">The course notebook</h2><span>01 — 05 / Read in order, revisit by topic</span></div>{rows}</section><section class="library-practice"><div><p class="panel-label">Start small. Make it observable.</p><h2>A lab you can run<br>before connecting a model.</h2></div><div><p>Every module has a self-contained Python exercise. Fixed fixtures make the control flow, outputs, and failure cases inspectable without API keys.</p><a class="button" href="chapters/module-1.html#code">Build your first workflow →</a></div></section><footer class="library-footer"><p>Based on Andrew Ng’s Agentic AI course. Course sources and teaching extensions are identified within each chapter.</p><div><a href="archive/2026-09-05/index.html">Archived edition ↗</a><a href="https://github.com/soumyadatascience/Agentic-AI-andrew-ng">Source repository ↗</a></div></footer></main></body></html>'''
    (ROOT/'index.html').write_text(html)
    print('Built index and five modules from notes/*.html')


if __name__ == '__main__':
    build()
