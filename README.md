# Adventní kalendář

Adventní herně šifrovací kalendář grafit.games. Tento repozitář je zdroj kalendáře;
web [grafit.games](https://grafit.games/) žije v repozitáři
[grafit-games-web](https://github.com/bremondr/grafit-games-web) a kalendář se do něj nasazuje automaticky.

**Repozitář je veřejný.** Nikdy sem neukládej hesla, řešení ani nešifrované obrázky a zprávy
(viz [Tajné věci](#tajné-věci)).

## Obsah

- `index.html`, `calendar.css`, `calendar.js`, `themes.js` – samotný kalendář (statický web bez buildu).
- `games/<den>/` – hra pro každý den (Unity WebGL build, `index.html` + `Build/` + `TemplateData/`).
- `images/<den>.json`, `messages/finale.json` – zašifrované obrázky a závěrečná zpráva.
- `encrypt-image.ps1`, `encrypt-message.ps1` – skripty, které z `private/` vyrobí zašifrované soubory výše (PowerShell).
- `private/` – **jen na tvém disku**, v `.gitignore`: hesla (`secret.csv`, `final-secret.csv`) a původní obrázky.
- `tools/build.py` – složí nasaditelnou podobu kalendáře; `tools/check.py` – kontrola odkazů, obsahu a motivů.
- `.github/workflows/` – `staging.yml` (testovací web) a `release.yml` (ostré nasazení).

## Jak to jede

```text
větev claude/<téma>  ──pull request──▶  main  ──automaticky──▶  STAGING
                                         │                bremondr.github.io/adventni-kalendar/
                                         │
                                         └──merge do──▶  release  ──automaticky──▶  grafit.games
                                                                     (commit do calendar/2026/ ve webu)
```

1. **Vývoj:** pracuj na vlastní větvi a otevři pull request do `main`. PR spustí build a kontrolu.
2. **Staging:** po sloučení do `main` se kalendář publikuje na
   <https://bremondr.github.io/adventni-kalendar/> (adresářová struktura jako na ostrém webu, takže
   relativní odkazy na `assets/` fungují stejně). Tady se testuje.
3. **Ostré nasazení:** až jste spokojení, sluč `main` do větve `release`. Workflow `release.yml`
   zkontroluje kalendář (přísněji, viz níže), nahradí `calendar/2026/` ve webovém repozitáři a
   commitne do jeho `main`; GitHub Pages ho pak vystaví na grafit.games.

Přísná kontrola před ostrým nasazením odmítne: vypnutý zámek data (`ENFORCE_SERVER_DATE_LIMIT`
v `calendar.js` musí být `true`), rozpracovanou kostru bez her a chybějící dny či finále.
Dokud je zámek `false`, staging je plně proklikatelný (hodí se pro testování), ale `release` neprojde.

Workflow `release.yml` používá tajný klíč `WEB_DEPLOY_KEY` (deploy key s právem zápisu jen do
`grafit-games-web`). Nasazení se dotkne pouze `calendar/2026/` ve webu.

## Lokální náhled

Potřebuješ Python 3 a kopii webu (kvůli sdíleným `assets/`):

```bash
git clone --depth 1 https://github.com/bremondr/grafit-games-web.git .web-cache
python tools/build.py --web .web-cache --out _site
python tools/check.py --site _site
python -m http.server 8080 --directory _site
```

Pak otevři <http://localhost:8080/calendar/2026/>. Se zámkem data vypnutým funguje `?day=15` a `?theme=theme-3`.

## Tajné věci

- Hesla a nešifrované podklady patří **jen** do `private/` (nikdy se necommitují; `tools/check.py` hlídá,
  že tam nic nesvítí).
- Zašifrované výstupy (`images/*.json`, `messages/finale.json`) se commitují. Po změně hesla nebo obrázku
  spusť příslušný `encrypt-*.ps1` a commitni nový výstup.
- Řešení šifer a seznam hesel si drž mimo repozitář (např. v soukromých poznámkách).

## Velikost

Hry jsou těžké (loni asi 440 MB za 24 dní). GitHub doporučuje držet repozitář i web Pages pod
zhruba 1 GB a soubor nesmí mít přes 100 MB. Věnujte tomu pozornost dřív, než přibude všech 24 her.

## Jak přispívat

- Před začátkem práce udělej `git pull`.
- Pracuj na vlastní větvi (`claude/<téma>` nebo jméno + téma) a do `main` ani `release` neposílej přímo;
  změny se slučují přes pull request.
- Commituj po malých krocích a s výstižnou zprávou.
- Standardní Markdown odkazy, UTF-8, LF; přílohy ukládej do tohoto repozitáře.
- Nepřidávej sem soukromé poznámky, přístupové údaje ani osobní data.
