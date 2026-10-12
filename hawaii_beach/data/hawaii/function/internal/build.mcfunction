# Bouwt het hele gebied. Wordt aangeroepen met storage hawaii:args (macro).
# Elke fill is max 1 laag hoog zodat hij onder de limiet van 32768 blokken blijft.

# 1. Gebied leegmaken (lucht) van ~0 tot ~40
$fill ~$(x0) ~0 ~$(z0) ~$(x1) ~0 ~$(z1) minecraft:air
$fill ~$(x0) ~1 ~$(z0) ~$(x1) ~1 ~$(z1) minecraft:air
$fill ~$(x0) ~2 ~$(z0) ~$(x1) ~2 ~$(z1) minecraft:air
$fill ~$(x0) ~3 ~$(z0) ~$(x1) ~3 ~$(z1) minecraft:air
$fill ~$(x0) ~4 ~$(z0) ~$(x1) ~4 ~$(z1) minecraft:air
$fill ~$(x0) ~5 ~$(z0) ~$(x1) ~5 ~$(z1) minecraft:air
$fill ~$(x0) ~6 ~$(z0) ~$(x1) ~6 ~$(z1) minecraft:air
$fill ~$(x0) ~7 ~$(z0) ~$(x1) ~7 ~$(z1) minecraft:air
$fill ~$(x0) ~8 ~$(z0) ~$(x1) ~8 ~$(z1) minecraft:air
$fill ~$(x0) ~9 ~$(z0) ~$(x1) ~9 ~$(z1) minecraft:air
$fill ~$(x0) ~10 ~$(z0) ~$(x1) ~10 ~$(z1) minecraft:air
$fill ~$(x0) ~11 ~$(z0) ~$(x1) ~11 ~$(z1) minecraft:air
$fill ~$(x0) ~12 ~$(z0) ~$(x1) ~12 ~$(z1) minecraft:air
$fill ~$(x0) ~13 ~$(z0) ~$(x1) ~13 ~$(z1) minecraft:air
$fill ~$(x0) ~14 ~$(z0) ~$(x1) ~14 ~$(z1) minecraft:air
$fill ~$(x0) ~15 ~$(z0) ~$(x1) ~15 ~$(z1) minecraft:air
$fill ~$(x0) ~16 ~$(z0) ~$(x1) ~16 ~$(z1) minecraft:air
$fill ~$(x0) ~17 ~$(z0) ~$(x1) ~17 ~$(z1) minecraft:air
$fill ~$(x0) ~18 ~$(z0) ~$(x1) ~18 ~$(z1) minecraft:air
$fill ~$(x0) ~19 ~$(z0) ~$(x1) ~19 ~$(z1) minecraft:air
$fill ~$(x0) ~20 ~$(z0) ~$(x1) ~20 ~$(z1) minecraft:air
$fill ~$(x0) ~21 ~$(z0) ~$(x1) ~21 ~$(z1) minecraft:air
$fill ~$(x0) ~22 ~$(z0) ~$(x1) ~22 ~$(z1) minecraft:air
$fill ~$(x0) ~23 ~$(z0) ~$(x1) ~23 ~$(z1) minecraft:air
$fill ~$(x0) ~24 ~$(z0) ~$(x1) ~24 ~$(z1) minecraft:air
$fill ~$(x0) ~25 ~$(z0) ~$(x1) ~25 ~$(z1) minecraft:air
$fill ~$(x0) ~26 ~$(z0) ~$(x1) ~26 ~$(z1) minecraft:air
$fill ~$(x0) ~27 ~$(z0) ~$(x1) ~27 ~$(z1) minecraft:air
$fill ~$(x0) ~28 ~$(z0) ~$(x1) ~28 ~$(z1) minecraft:air
$fill ~$(x0) ~29 ~$(z0) ~$(x1) ~29 ~$(z1) minecraft:air
$fill ~$(x0) ~30 ~$(z0) ~$(x1) ~30 ~$(z1) minecraft:air
$fill ~$(x0) ~31 ~$(z0) ~$(x1) ~31 ~$(z1) minecraft:air
$fill ~$(x0) ~32 ~$(z0) ~$(x1) ~32 ~$(z1) minecraft:air
$fill ~$(x0) ~33 ~$(z0) ~$(x1) ~33 ~$(z1) minecraft:air
$fill ~$(x0) ~34 ~$(z0) ~$(x1) ~34 ~$(z1) minecraft:air
$fill ~$(x0) ~35 ~$(z0) ~$(x1) ~35 ~$(z1) minecraft:air
$fill ~$(x0) ~36 ~$(z0) ~$(x1) ~36 ~$(z1) minecraft:air
$fill ~$(x0) ~37 ~$(z0) ~$(x1) ~37 ~$(z1) minecraft:air
$fill ~$(x0) ~38 ~$(z0) ~$(x1) ~38 ~$(z1) minecraft:air
$fill ~$(x0) ~39 ~$(z0) ~$(x1) ~39 ~$(z1) minecraft:air
$fill ~$(x0) ~40 ~$(z0) ~$(x1) ~40 ~$(z1) minecraft:air

# 2. Ondergrond: steenlaag + zand
$fill ~$(x0) ~-8 ~$(z0) ~$(x1) ~-8 ~$(z1) minecraft:stone
$fill ~$(x0) ~-7 ~$(z0) ~$(x1) ~-7 ~$(z1) minecraft:sand
$fill ~$(x0) ~-6 ~$(z0) ~$(x1) ~-6 ~$(z1) minecraft:sand
$fill ~$(x0) ~-5 ~$(z0) ~$(x1) ~-5 ~$(z1) minecraft:sand
$fill ~$(x0) ~-4 ~$(z0) ~$(x1) ~-4 ~$(z1) minecraft:sand
$fill ~$(x0) ~-3 ~$(z0) ~$(x1) ~-3 ~$(z1) minecraft:sand
$fill ~$(x0) ~-2 ~$(z0) ~$(x1) ~-2 ~$(z1) minecraft:sand
$fill ~$(x0) ~-1 ~$(z0) ~$(x1) ~-1 ~$(z1) minecraft:sand

# 3. Zee: diep -> middel -> ondiep naar het strand toe
$fill ~$(x0) ~-5 ~$(z0) ~$(deepE) ~-1 ~$(z1) minecraft:water
$fill ~$(midS) ~-3 ~$(z0) ~$(midE) ~-1 ~$(z1) minecraft:water
$fill ~$(shS) ~-1 ~$(z0) ~$(shE) ~-1 ~$(z1) minecraft:water

# 4. Jungle-grond achter het strand
$fill ~$(jS) ~-3 ~$(z0) ~$(x1) ~-2 ~$(z1) minecraft:dirt
$fill ~$(jS) ~-1 ~$(z0) ~$(x1) ~-1 ~$(z1) minecraft:grass_block

# 5. Heuvels op de achtergrond (3 treden)
$fill ~$(h1) ~-1 ~$(z0) ~$(x1) ~1 ~$(z1) minecraft:dirt
$fill ~$(h1) ~2 ~$(z0) ~$(x1) ~2 ~$(z1) minecraft:grass_block
$fill ~$(h2) ~2 ~$(z0) ~$(x1) ~4 ~$(z1) minecraft:dirt
$fill ~$(h2) ~5 ~$(z0) ~$(x1) ~5 ~$(z1) minecraft:grass_block
$fill ~$(h3) ~5 ~$(z0) ~$(x1) ~7 ~$(z1) minecraft:dirt
$fill ~$(h3) ~8 ~$(z0) ~$(x1) ~8 ~$(z1) minecraft:grass_block

# 6. Tiki bar in het midden van het strand (eerst, zodat palmen er niet doorheen groeien)
function hawaii:internal/tiki_bar

# 7. Zee-decoratie: koraal, zeegras, zeekomkommers, tropische vissen
scoreboard players operation #cols hw = #ocols hw
scoreboard players operation #r hw = #orows hw
data modify storage hawaii:tmp set value {deco:"ocean",hm:"ocean_floor",step:5}
$execute positioned ~$(oGX) ~ ~$(gZ) run function hawaii:grid/rows with storage hawaii:tmp

# 8. Strand-decoratie: palmbomen, parasols, schildpadden
scoreboard players operation #cols hw = #bcols hw
scoreboard players operation #r hw = #brows hw
data modify storage hawaii:tmp set value {deco:"beach",hm:"motion_blocking_no_leaves",step:6}
$execute positioned ~$(bGX) ~ ~$(gZ) run function hawaii:grid/rows with storage hawaii:tmp

# 9. Jungle + heuvels: bomen, bamboe, struiken, bloemen, papegaaien
scoreboard players operation #cols hw = #jcols hw
scoreboard players operation #r hw = #jrows hw
data modify storage hawaii:tmp set value {deco:"jungle",hm:"motion_blocking_no_leaves",step:5}
$execute positioned ~$(jGX) ~ ~$(gZ) run function hawaii:grid/rows with storage hawaii:tmp

# 10. Afronden
kill @e[type=minecraft:marker,tag=hawaii_bar]
tp @s[type=minecraft:player] ~0.5 ~ ~-5.5 0 0
tellraw @a[distance=..256] [{"text":"Aloha! ","color":"gold","bold":true},{"text":"Hawaii strand gebouwd: ","color":"yellow","bold":false},{"score":{"name":"#chunks","objective":"hw"},"color":"aqua"},{"text":" x ","color":"aqua"},{"score":{"name":"#chunks","objective":"hw"},"color":"aqua"},{"text":" chunks","color":"aqua"}]
