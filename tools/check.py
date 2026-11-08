#!/usr/bin/env python3
"""Smoke check for the advent calendar (stdlib only).

  python tools/check.py --site _site            # after: python tools/build.py --web ... --out _site
  python tools/check.py --site _site --release  # the stricter check before going live

Verifies that
  1. every local reference (href/src/url()) in the site's HTML and CSS resolves to a file,
  2. when the calendar is populated, every day has its game, its encrypted image and the finale message,
  3. the themes in themes.js start at day 1 and have a palette block in calendar.css,
  4. nothing from private/ is tracked by git (this repo is public).
With --release it also requires that the date lock is on and that all 24 days are populated.
Exit code 1 on any problem.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "private", "node_modules", "TemplateData", "Build"}
REF_RE = re.compile(r"""(?:href|src)\s*=\s*["']([^"'#?][^"']*)["']|url\(\s*["']?([^"')]+)["']?\s*\)""", re.I)
problems = []


def local_target(site: Path, source: Path, ref: str):
    if ref.startswith(("data:", "http:", "https:", "//", "mailto:", "javascript:")):
        return None
    path = unquote(urlparse(ref).path)
    if not path:
        return None
    base = site if path.startswith("/") else source.parent
    return (base / path.lstrip("/")).resolve()


def check_refs(site: Path) -> int:
    files = [p for ext in ("*.html", "*.css") for p in site.rglob(ext)
             if not SKIP_DIRS & set(p.relative_to(site).parts)]
    for f in files:
        text = f.read_text(encoding="utf-8-sig", errors="replace")
        for m in REF_RE.finditer(text):
            ref = m.group(1) or m.group(2)
            target = local_target(site, f, ref.strip())
            if target is None:
                continue
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                problems.append(f"{f.relative_to(site)}: missing '{ref}'")
    return len(files)


def populated() -> bool:
    return any(d.is_dir() for d in (ROOT / "games").glob("*"))


def check_content(release: bool):
    if not populated():
        if release:
            problems.append("release: no games yet, the calendar is still a skeleton")
        else:
            print("  skeleton (no games yet), skipped content check")
        return
    for day in range(1, 25):
        if not (ROOT / "images" / f"{day}.json").exists():
            problems.append(f"missing images/{day}.json")
        if not (ROOT / "games" / str(day)).is_dir():
            problems.append(f"missing games/{day}/")
    if not (ROOT / "messages" / "finale.json").exists():
        problems.append("missing messages/finale.json")


def check_themes():
    text = (ROOT / "themes.js").read_text(encoding="utf-8-sig")
    found = re.findall(r'id:\s*"([^"]+)"\s*,\s*name:[^,]+,\s*startDay:\s*(\d+)', text)
    ids, starts = [i for i, _ in found], [int(d) for _, d in found]
    if not found or starts[0] != 1 or starts != sorted(set(starts)) or starts[-1] > 24:
        problems.append("themes.js: themes must start at day 1 with ascending startDay <= 24")
    css = (ROOT / "calendar.css").read_text(encoding="utf-8-sig")
    for theme_id in ids:
        if f'[data-theme="{theme_id}"]' not in css:
            problems.append(f"calendar.css: no palette block for {theme_id}")


def check_private():
    out = subprocess.run(["git", "ls-files", "--cached"], cwd=ROOT,
                         capture_output=True, text=True).stdout.splitlines()
    leaked = [p for p in out if p.startswith("private/") or "/private/" in p]
    if leaked:
        problems.append(f"private files are tracked/staged ({len(leaked)}), e.g. {leaked[0]}")


def check_release():
    js = (ROOT / "calendar.js").read_text(encoding="utf-8-sig")
    if not re.search(r"const\s+ENFORCE_SERVER_DATE_LIMIT\s*=\s*true\b", js):
        problems.append("release: ENFORCE_SERVER_DATE_LIMIT must be true in calendar.js")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--site", required=True, help="assembled site folder (from tools/build.py --web)")
    parser.add_argument("--release", action="store_true", help="stricter checks before going live")
    args = parser.parse_args()

    n = check_refs(Path(args.site).resolve())
    check_content(args.release)
    check_themes()
    check_private()
    if args.release:
        check_release()
    print(f"checked {n} html/css files")
    if problems:
        print("\nFAILED:")
        print("\n".join(f"  - {p}" for p in problems))
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
