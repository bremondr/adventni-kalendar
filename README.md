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
- `tools/build.py` – složí nasaditelnou podobu kalendáře (volitelně jen dny do `--through-day`);
  `tools/check.py` – kontrola odkazů, obsahu a motivů; `tools/unlock.py` – které dny jsou dnes otevřené.
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

### Postupné odemykání: na web jdou jen dny, které už nastaly

Na ostrý web se nikdy nenasadí hra dne, který ještě nenastal (pražský čas):

- `release.yml` běží při každém pushi do `release` **a každou hodinu v prosinci**, takže nový den se
  objeví krátce po půlnoci. Když se nic nezměnilo, nic se necommituje.
- Obsah bere vždy z větve `release`. Do webu se zkopírují jen `games/<den>/` a `images/<den>.json`
  pro dny `1..dnes`; finále (`messages/finale.json`) až 24. 12. Do 1. 12. nejde na web žádný den,
  od 25. 12. všech 24.
- Hry tedy stačí mít ve větvi `release` **před** jejich datem. Co tam ještě není, se prostě nenasadí.
- Plánované běhy používají kopii `release.yml` z větve `main`, proto držte `main` a `release` pohromadě
  (sluč `main` do `release`, ne naopak).

Přísná kontrola před ostrým nasazením odmítne: vypnutý zámek data (`ENFORCE_SERVER_DATE_LIMIT`
v `calendar.js` musí být `true`), chybějící nebo rozdělanou hru či obrázek u dne, který už nastal,
a chybějící finále od 24. 12. Dny, které ještě nenastaly, smí chybět. Na stagingu kontrola jen hlídá,
aby žádný den nebyl rozdělaný (hra bez obrázku nebo naopak). Dokud je zámek `false`, staging je plně
proklikatelný (hodí se pro testování), ale `release` neprojde.

Lokálně: `python tools/build.py --out dist --through-day auto` vyrobí to, co by se dnes nasadilo.
S `--through-day 5` (nebo jiným číslem) si vyzkoušíš, co by se nasadilo v ten den.

### Pozor: repozitář a staging jsou veřejné

Hry budoucích dnů v `main` a na stagingu uvidí každý, kdo adresu najde. Ostrý web je před datem
nezveřejní, ale tento repozitář ano. Pokud má být hra překvapením, přidej ji do `main` (a do `release`)
až těsně před jejím dnem. Obrázky a finále jsou zašifrované, hry ne.

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
zhruba 1 GB a soubor nesmí mít přes 100 MB. Postupné nasazování to trochu zmírní (do webu se hry
přidávají po dnech), ale repozitář webu roste i tak; věnujte tomu pozornost dřív, než přibude všech 24 her.

## Jak přispívat

- Před začátkem práce udělej `git pull`.
- Pracuj na vlastní větvi (`claude/<téma>` nebo jméno + téma) a do `main` ani `release` neposílej přímo;
  změny se slučují přes pull request.
- Commituj po malých krocích a s výstižnou zprávou.
- Standardní Markdown odkazy, UTF-8, LF; přílohy ukládej do tohoto repozitáře.
- Nepřidávej sem soukromé poznámky, přístupové údaje ani osobní data.
