"""Check local links, generated-page consistency, and runnable exercises."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.refs, self.copy_targets = [], [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if "data-copy" in attrs:
            self.copy_targets.append(attrs["data-copy"])
        for key in ("href", "src"):
            if key in attrs:
                self.refs.append(attrs[key])


def check():
    active = [ROOT / "index.html", *sorted((ROOT / "chapters").glob("*.html"))]
    before = {f: f.read_bytes() for f in active}
    subprocess.run([sys.executable, str(ROOT / "scripts/build_site.py")], check=True)
    assert all(f.read_bytes() == content for f, content in before.items()), "Generated pages were stale; inspect the rebuild and rerun."
    files = active + list((ROOT / "archive").rglob("*.html")) + [ROOT / "preview/index.html"]
    pages = {}
    for file in files:
        page = Page()
        page.feed(file.read_text())
        assert all(count == 1 for count in Counter(page.ids).values()), f"Duplicate IDs: {file}"
        assert all(target in page.ids for target in page.copy_targets), f"Missing clipboard target: {file}"
        pages[file.resolve()] = page
    for file, page in pages.items():
        for ref in page.refs:
            parsed = urlsplit(ref)
            if parsed.scheme or parsed.netloc:
                continue
            target = (file.parent / unquote(parsed.path)).resolve() if parsed.path else file
            assert target.exists(), f"Missing local target: {file}: {ref}"
            if parsed.fragment and target in pages:
                assert unquote(parsed.fragment) in pages[target].ids, f"Missing anchor: {file}: {ref}"
    print("PASS: reproducible build; active/archive links, assets, anchors, and copy targets")
    for lab in sorted((ROOT / "labs").glob("module_*.py")):
        result = subprocess.run([sys.executable, str(lab)], capture_output=True, text=True)
        assert result.returncode == 0, f"{lab.name}: {result.stderr}"
        print(f"PASS: {lab.name}")


if __name__ == "__main__":
    check()
