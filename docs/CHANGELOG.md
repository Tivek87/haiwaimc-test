# Changelog

Alle wijzigingen aan de Hawaii Beach datapack.
Elke versie hieronder wordt automatisch gepubliceerd op de
[Releases-pagina](https://github.com/tivek87/haiwaimc-test/releases) met de zip als download.

Tijden zijn in UTC.

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
