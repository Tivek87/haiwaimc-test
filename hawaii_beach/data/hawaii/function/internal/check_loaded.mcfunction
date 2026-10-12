# Zet #loaded op 1 als alle 4 hoeken van het gebied geladen zijn
$execute if loaded ~$(x0) ~ ~$(z0) if loaded ~$(x1) ~ ~$(z1) if loaded ~$(x0) ~ ~$(z1) if loaded ~$(x1) ~ ~$(z0) run scoreboard players set #loaded hw 1
