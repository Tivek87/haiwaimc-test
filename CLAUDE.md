# Werkafspraken

## ALTIJD een nieuwe release na ELKE wijziging

Elke wijziging die je pusht, hoe klein ook (datapack, tools, docs, workflow, deze file),
krijgt een nieuwe versie en een GitHub-release. Nooit pushen zonder versie-ophoging.
De release-workflow faalt (rood) als er gepusht wordt zonder nieuw versienummer.

Stappen, elke keer:

1. `python3 scripts/bump_version.py "korte bullet" "nog een bullet"` (Nederlands).
   Dit verhoogt de versie in `hawaii_beach/pack.mcmeta` en zet bovenaan `docs/CHANGELOG.md`
   een entry `## [x.y.z] - JJJJ-MM-DD UU:MM UTC` met de bullets.
2. Commit alles samen (wijziging + versie + changelog) en push.
3. Controleer dat de workflow "Release datapack" groen is en dat release `vx.y.z`
   met de zip op de Releases-pagina staat. Meld de link aan de gebruiker.

## Versienummers

Elke update verhoogt de versie met precies 1 stap, elk deel loopt van 0 t/m 99:

    v0.0.1 -> v0.0.2 -> ... -> v0.0.99 -> v0.1.0 -> ... -> v0.99.99 -> v1.0.0 -> ... -> v99.99.99 (max)

Nooit zelf een deel overslaan of een "minor"/"major" bump kiezen: altijd +1 op het laatste deel,
met overloop naar het volgende deel na 99. Gebruik daarvoor altijd `scripts/bump_version.py`.

Geen zip in de repo committen; de zip komt van de Releases-pagina.

## Gegenereerde bestanden

`hawaii_beach/data/hawaii/structure/`, `function/gen/` en `worldgen/` worden gemaakt door
`python3 tools/generate.py` (stranden 1-8 chunks) en `python3 tools/island_generate.py` (eiland 36x36,
heeft numpy nodig). Ze staan in `.gitignore`; de release-workflow genereert ze opnieuw.
Test lokaal altijd beide generators (ze controleren elk blok/entity tegen `tools/mcdata_1.21.1.json`)
en bekijk de voorbeelden met `--preview` (komen in `tools/preview/`, niet committen).
