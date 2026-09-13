# luneo.no

Markedssiden for bookingsystemet Luneo. Statisk side, publiseres med Cloudflare Pages
(prosjekt «luneo-no», ingen byggesteg, utdatamappe `/`). Push til `main` = ny deploy.

## Sider

- Norsk (standard): `index.html`, `personvern.html`, `kjopsvilkar.html`
- Engelsk: `en/index.html`, `en/privacy.html`, `en/terms.html`
- Flaggvelger i toppen bytter mellom språkene.

## Slik endrer du innholdet

Ikke rediger HTML-filene i roten direkte – de er generert. Rediger i `kilde/` og bygg:

```
cd kilde
python build.py
```

`build.py` leser `body.nb.html`, `body.en.html` og `style.css`, og skriver
sidene til `site/`. Kopier innholdet i `site/` til roten (og `site/en/` til `en/`),
commit og push.

`kilde/makevideo.py` lager bakgrunnsfilmen `img/bakgrunn.mp4` (+ `bakgrunn.jpg`).
`kilde/luneo-presentasjon.html` er én selvstendig fil med begge språk og alt innbygd –
til bruk som presentasjon/vedlegg.
