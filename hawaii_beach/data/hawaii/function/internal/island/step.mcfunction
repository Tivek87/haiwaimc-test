# Bouwt chunk #i als die geladen is (as/at de markering)
execute if score #i hw >= #total hw run return 0
scoreboard players operation #px hw = #i hw
scoreboard players operation #px hw %= #n hw
scoreboard players operation #px hw *= #16 hw
scoreboard players operation #px hw += #x0 hw
scoreboard players operation #pz hw = #i hw
scoreboard players operation #pz hw /= #n hw
scoreboard players operation #pz hw *= #16 hw
scoreboard players operation #pz hw += #x0 hw
execute store result storage hawaii:isl px int 1 run scoreboard players get #px hw
execute store result storage hawaii:isl pz int 1 run scoreboard players get #pz hw
execute store result storage hawaii:isl i int 1 run scoreboard players get #i hw
scoreboard players set #ok hw 0
function hawaii:internal/island/check with storage hawaii:isl
# nog niet geladen: wachten (max ~15 seconden per chunk)
execute if score #ok hw matches 0 run scoreboard players add #wait hw 1
execute if score #ok hw matches 0 if score #wait hw matches ..900 run return 0
scoreboard players set #wait hw 0
function hawaii:internal/island/place with storage hawaii:isl
scoreboard players add #i hw 1
