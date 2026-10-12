# Changelog

Alle wijzigingen aan de Hawaii Beach datapack.
Elke versie hieronder wordt automatisch gepubliceerd op de
[Releases-pagina](https://github.com/tivek87/haiwaimc-test/releases) met de zip als download.

Tijden zijn in UTC.

Versienummers gaan per update 1 stap omhoog: v0.0.1 -> v0.0.2 ... v0.0.99 -> v0.1.0 ...
v0.99.99 -> v1.0.0 ... tot maximaal v99.99.99. (v1.0.0 t/m v1.2.0 zijn van voor deze afspraak.)

## [1.2.2] - 2026-10-12 23:57 UTC

- Volledig nieuw ontwerp: alles wordt per chunk als structuur geplaatst (python3 tools/generate.py ontwerpt elk blok)
- Grote tiki bar (4+ chunks): rieten dak met glow berries, U-bar met krukken, achterbar, keuken, podium met hula dansers, tafels, totems, zwevend bord
- 3 bartenders met 6 cocktails met echte effecten (Pina Colada, Blue Hawaii, Mai Tai, Lava Flow, Coconut Kiss, Lagoon Punch) en eten
- Natuurlijke kustlijn, turquoise warm-ocean water, koraalrif, kelp, zeegras, vissen en dolfijnen
- Vulkaan met lavameer, magma-stromen en rookpluimen; lagune met waterval, waterlelies, axolotls en kikkers
- Steiger met bootjes en visser, hutten, vuurplaats, strandwacht-toren, volleybalveld, zandkastelen, parasols met ligstoelen en surfplanken
- Gebogen palmen met kokosnoten, reuzen-junglebomen met lianen, bamboebossen, bloemen, papegaaien, ocelots en panda's
- Terrein loopt aan de randen af zodat het aansluit op de wereld; biomen worden aangepast; geen monsters door lichtblokken
- Elk blok en elke entity is gecontroleerd tegen de officiele 1.21.1 lijsten

## [1.2.1] - 2026-10-12 23:53 UTC

- Afspraak: na elke wijziging (hoe klein ook) altijd een nieuwe versie en release
- Release-workflow draait nu bij elke push en wordt rood als er gepusht wordt zonder nieuw versienummer

## [1.2.0] - 2026-10-12 23:22 UTC

- Voortgangsbalk (bossbar) bovenin beeld met percentage en wat er gebouwd wordt
- Bouwen gaat nu in stapjes over meerdere ticks, zodat de game niet meer bevriest (4x4 chunks duurt ~2 sec, 8x8 ~3 sec)
- Het strand wordt altijd gebouwd op de plek waar de speler stond bij het starten, ook als je tijdens het bouwen wegloopt
- Chunks worden tijdens het bouwen geladen gehouden (forceload) en daarna weer vrijgegeven
- Lucht wordt van boven naar beneden gemaakt, zodat zand en grind niet meer naar beneden vallen
- Chatbericht bij start en bij klaar

## [1.1.0] - 2026-10-12 23:20 UTC

- Fix: `/function hawaii:beach` zonder argumenten gaf "Missing arguments"; bouwt nu standaard 4x4 chunks
- Nieuw: `/function hawaii:beach_1` t/m `hawaii:beach_8` voor elke grootte, zonder `{chunks:N}` te typen
- De versie met argument heet nu `/function hawaii:generate {chunks:N}`

## [1.0.0] - 2026-10-12 23:05 UTC

- Eerste versie van de datapack voor Minecraft (NeoForge) 1.21.1
- `/function hawaii:beach {chunks:N}` bouwt een strand van 1 t/m 8 chunks rond de speler
- Zee met diep/ondiep water, koraal, zeegras, kelp en tropische vissen
- Strand met rechte en schuine palmbomen (met kokosnoten), parasols en schildpadden
- Tiki bar met rieten dak, bar, krukken, fakkels, naambord en een papegaai
- Barman "Kai" (villager) verkoopt Pina Colada, Blue Hawaii, Mai Tai en meloen
- Jungle en heuvels op de achtergrond met bomen, bamboe, bloemen, papegaaien en ocelots
- Automatische GitHub-release bij elke nieuwe versie in deze changelog
