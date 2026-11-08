# Adventní kalendář: instructions for agents

- This repo is **public**. Never commit passwords, solutions or unencrypted images/messages.
  Those live in `private/` (gitignored) or outside the repo.
- Work on a branch `claude/<short-topic>` and open a pull request. Never push to `main` or
  `release`, never force-push.
- A merge to `main` publishes the staging site. A push or merge to `release` puts the calendar
  live on grafit.games (commits to `calendar/2026/` in `bremondr/grafit-games-web`). Only the
  owner decides when. Never create or push the `release` branch yourself.
- Before a commit: `python tools/build.py --web <grafit-games-web checkout> --out _site` and
  `python tools/check.py --site _site` must pass (see README, "Lokální náhled").
- Do not add links from this repo to private notes of the owner.
