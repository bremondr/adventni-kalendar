#!/usr/bin/env python3
"""Assemble the advent calendar for staging or for release (stdlib only).

Two modes:

  python tools/build.py --out dist
      Writes only the deployable calendar files to dist/. The release workflow
      uses this to fill calendar/<year>/ in the website repo.

  python tools/build.py --web <checkout of grafit-games-web> --out _site
      Writes a whole site tree: the website's shared assets/ plus the calendar at
      calendar/<year>/, and a root index.html that redirects there. The staging
      workflow publishes this, and it has the same URL layout as grafit.games,
      so the calendar's relative links (../../assets/...) work in both places.

Only the files listed below are deployed. private/, tools/, the encrypt scripts
and everything else stay in this repo.
"""
import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YEAR = "2026"
FILES = ["index.html", "calendar.css", "calendar.js", "themes.js"]
DIRS = ["games", "images", "messages"]
REDIRECT = (
    '<!DOCTYPE html>\n<meta charset="utf-8">\n<title>Staging</title>\n'
    '<meta http-equiv="refresh" content="0; url=calendar/{year}/">\n'
    '<a href="calendar/{year}/">Adventní kalendář {year} (staging)</a>\n'
)


def copy_calendar(target: Path) -> int:
    target.mkdir(parents=True, exist_ok=True)
    count = 0
    for name in FILES:
        shutil.copy2(ROOT / name, target / name)
        count += 1
    for name in DIRS:
        src = ROOT / name
        if not src.is_dir():
            continue
        for path in sorted(src.rglob("*")):
            if path.is_dir() or path.name == ".gitkeep":
                continue
            dest = target / path.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True, help="output folder (is emptied first)")
    parser.add_argument("--web", help="checkout of grafit-games-web; builds a whole site tree")
    parser.add_argument("--year", default=YEAR)
    args = parser.parse_args()

    out = Path(args.out).resolve()
    if out == ROOT or ROOT in out.parents and out.name in {"games", "images", "messages", "tools"}:
        print(f"refusing to write into {out}", file=sys.stderr)
        return 1
    if out.exists():
        shutil.rmtree(out)

    if args.web:
        web = Path(args.web).resolve()
        if not (web / "assets").is_dir():
            print(f"{web} has no assets/ folder; is it a grafit-games-web checkout?", file=sys.stderr)
            return 1
        shutil.copytree(web / "assets", out / "assets")
        count = copy_calendar(out / "calendar" / args.year)
        (out / "index.html").write_text(REDIRECT.format(year=args.year), encoding="utf-8")
    else:
        count = copy_calendar(out)
    print(f"built {out} ({count} calendar files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
