# Werkafspraken

## Versienummers

Elke update verhoogt de versie met precies 1 stap, elk deel loopt van 0 t/m 99:

    v0.0.1 -> v0.0.2 -> ... -> v0.0.99 -> v0.1.0 -> ... -> v0.99.99 -> v1.0.0 -> ... -> v99.99.99 (max)

Dus nooit zelf een deel overslaan of een "minor"/"major" bump kiezen: altijd +1 op het laatste deel,
met overloop naar het volgende deel na 99. Gebruik daarvoor `scripts/bump_version.py`.

## Bij elke wijziging aan de datapack (`hawaii_beach/`)

1. Run `python3 scripts/bump_version.py "korte bullet" "nog een bullet"` (Nederlands).
   Dit verhoogt de versie in `hawaii_beach/pack.mcmeta` en zet bovenaan `docs/CHANGELOG.md`
   een entry `## [x.y.z] - JJJJ-MM-DD UU:MM UTC` met de bullets.
2. Commit en push. `.github/workflows/release.yml` controleert de versie en maakt automatisch een
   GitHub-release `vx.y.z` met de zip en de changelog-entry als release notes.
3. Controleer daarna of de workflow geslaagd is en de release op de Releases-pagina staat.

Geen zip in de repo committen; de zip komt van de Releases-pagina.
