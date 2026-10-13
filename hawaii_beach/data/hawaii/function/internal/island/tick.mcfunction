# Elke tick: tot 3 chunks bouwen (alleen als ze geladen zijn)
execute unless entity @e[type=minecraft:marker,tag=hawaii_origin_island] run return run bossbar remove hawaii:progress
execute as @e[type=minecraft:marker,tag=hawaii_origin_island,limit=1] at @s run function hawaii:internal/island/step
execute as @e[type=minecraft:marker,tag=hawaii_origin_island,limit=1] at @s run function hawaii:internal/island/step
execute as @e[type=minecraft:marker,tag=hawaii_origin_island,limit=1] at @s run function hawaii:internal/island/step
function hawaii:internal/island/progress
execute if score #i hw >= #total hw as @e[type=minecraft:marker,tag=hawaii_origin_island,limit=1] at @s run return run function hawaii:internal/island/finish
schedule function hawaii:internal/island/tick 1t
