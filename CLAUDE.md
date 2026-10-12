# Werkafspraken

## Bij elke wijziging aan de datapack (`hawaii_beach/`)

1. Verhoog de versie (semver: x.y.z) in de `description` van `hawaii_beach/pack.mcmeta`.
2. Zet bovenaan `docs/CHANGELOG.md` een nieuwe entry:
   `## [x.y.z] - JJJJ-MM-DD UU:MM UTC` met korte bullets (Nederlands) van wat er veranderd is.
3. Commit en push. `.github/workflows/release.yml` maakt dan automatisch een GitHub-release
   `vx.y.z` met de zip en de changelog-entry als release notes.
4. Controleer daarna of de workflow geslaagd is en de release op de Releases-pagina staat.

Geen zip in de repo committen; de zip komt van de Releases-pagina.
