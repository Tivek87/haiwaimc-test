# Ondergrond van onder naar boven: y-8 steen, y-7 t/m y-1 zand
scoreboard players operation #y hw = #i hw
scoreboard players remove #y hw 49
execute store result storage hawaii:args y int 1 run scoreboard players get #y hw
data modify storage hawaii:args block set value "minecraft:sand"
execute if score #y hw matches -8 run data modify storage hawaii:args block set value "minecraft:stone"
function hawaii:internal/layer with storage hawaii:args
