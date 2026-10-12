# Lucht maken, van boven (y+40) naar beneden (y+0) zodat zand/grind niet naar beneden valt
scoreboard players set #y hw 40
scoreboard players operation #y hw -= #i hw
execute store result storage hawaii:args y int 1 run scoreboard players get #y hw
data modify storage hawaii:args block set value "minecraft:air"
function hawaii:internal/layer with storage hawaii:args
