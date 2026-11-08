#!/usr/bin/env python3
"""Assemble the advent calendar for staging or for release (stdlib only).

Two modes:

  python tools/build.py --out dist --through-day auto
      Writes only the deployable calendar files to dist/. The release workflow
      uses this to fill calendar/<year>/ in the website repo.

  python tools/build.py --web <checkout of grafit-games-web> --out _site
      Writes a whole site tree: the website's shared assets/ plus the calendar at
      calendar/<year>/, and a root index.html that redirects there. The staging
      workflow publishes this, and it has the same URL layout as grafit.games,
      so the calendar's relative links (../../assets/...) work in both places.

--through-day limits which days are included: a number, 'all' (default) or
'auto' (the days open today in Prague, see tools/unlock.py). Files of days after
that never leave this repo; messages/finale.json is included from day 24.

Only the files listed below are deployed. private/, tools/, the encrypt scripts
and everything else stay in this repo.
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # also works with python -I
import unlock  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
YEAR = str(unlock.YEAR)
FILES = ["index.html", "calendar.css", "calendar.js", "themes.js"]
DIRS = ["games", "images", "messages"]
REDIRECT = (
    '<!DOCTYPE html>\n<meta charset="utf-8">\n<title>Staging</title>\n'
    '<meta http-equiv="refresh" content="0; url=calendar/{year}/">\n'
    '<a href="calendar/{year}/">Adventní kalendář {year} (staging)</a>\n'
)


def day_of(rel: Path):
    """The day a file belongs to (games/7/..., images/7.json), 24 for the finale, else None."""
    top, rest = rel.parts[0], rel.parts[1:]
    if top == "games" and rest and rest[0].isdigit():
        return int(rest[0])
    if top == "images" and rest and rest[0].split(".")[0].isdigit():
        return int(rest[0].split(".")[0])
    if top == "messages" and rest and rest[0] == "finale.json":
        return unlock.LAST_DAY
    return None


def copy_calendar(target: Path, through: int) -> int:
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
            rel = path.relative_to(ROOT)
            day = day_of(rel)
            if day is not None and day > through:
                continue
            dest = target / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True, help="output folder (is emptied first)")
    parser.add_argument("--web", help="checkout of grafit-games-web; builds a whole site tree")
    parser.add_argument("--year", default=YEAR)
    parser.add_argument("--through-day", default="all", help="a number, 'all' (default) or 'auto' (today, Prague)")
    args = parser.parse_args()

    through = unlock.resolve(args.through_day)
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
        count = copy_calendar(out / "calendar" / args.year, through)
        (out / "index.html").write_text(REDIRECT.format(year=args.year), encoding="utf-8")
    else:
        count = copy_calendar(out, through)
    print(f"built {out} ({count} calendar files, days 1..{through})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
