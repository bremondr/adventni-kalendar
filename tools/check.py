#!/usr/bin/env python3
"""Smoke check for the advent calendar (stdlib only).

  python tools/check.py --site _site            # after: python tools/build.py --web ... --out _site
  python tools/check.py --site _site --release  # the stricter check before going live

Verifies that
  1. every local reference (href/src/url()) in the site's HTML and CSS resolves to a file,
  2. no day is half-done (a game without its encrypted image, or the other way round),
  3. the themes in themes.js start at day 1 and have a palette block in calendar.css,
  4. nothing from private/ is tracked by git (this repo is public).
With --release it also requires that the date lock is on, and that every day open today
(Prague time, or --through-day N) is complete, plus the finale from day 24. Days that are
not open yet may be missing: the calendar is released a few days at a time.
Exit code 1 on any problem.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))  # also works with python -I
import unlock  # noqa: E402

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


def has_game(day: int) -> bool:
    return (ROOT / "games" / str(day) / "index.html").is_file()


def has_image(day: int) -> bool:
    return (ROOT / "images" / f"{day}.json").is_file()


def check_content(through: int | None):
    """Rolling content check.

    Staging (through is None): a day may be missing entirely, but not half-done
    (a game without its image, or an image without its game).
    Release: every day up to `through` (the days open today) must be complete, and
    the finale from day 24. Days after that may be missing; they are only reported.
    """
    if through is None:
        for day in range(1, unlock.LAST_DAY + 1):
            if has_game(day) != has_image(day):
                what = "games/%d/index.html" % day if has_game(day) else "images/%d.json" % day
                problems.append(f"day {day} is half-done: only {what} exists")
        return
    for day in range(1, through + 1):
        if not has_game(day):
            problems.append(f"release: day {day} is open but games/{day}/index.html is missing")
        if not has_image(day):
            problems.append(f"release: day {day} is open but images/{day}.json is missing")
    if through >= unlock.LAST_DAY and not (ROOT / "messages" / "finale.json").is_file():
        problems.append("release: all days are open but messages/finale.json is missing")
    pending = [d for d in range(through + 1, unlock.LAST_DAY + 1) if not (has_game(d) and has_image(d))]
    print(f"  days open today: 1..{through}")
    if pending:
        print(f"  not ready yet, and not published yet: {', '.join(map(str, pending))}")


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
    parser.add_argument("--through-day", default="auto",
                        help="with --release: a number or 'auto' (the days open today in Prague, the default)")
    args = parser.parse_args()

    n = check_refs(Path(args.site).resolve())
    check_content(unlock.resolve(args.through_day) if args.release else None)
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
