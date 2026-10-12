# Wordt elke tick opnieuw ingepland totdat het strand klaar is.
execute unless entity @e[type=minecraft:marker,tag=hawaii_origin] run return run bossbar remove hawaii:progress

# eerst wachten tot de chunks geladen zijn (max 10 seconden)
execute if score #loaded hw matches 0 run scoreboard players add #wait hw 1
execute if score #loaded hw matches 0 as @e[type=minecraft:marker,tag=hawaii_origin,limit=1] at @s run function hawaii:internal/check_loaded with storage hawaii:args
execute if score #loaded hw matches 0 if score #wait hw matches 200.. run scoreboard players set #loaded hw 1
execute if score #loaded hw matches 0 run return run schedule function hawaii:internal/tick 1t

# 2 bouwstappen per tick
execute as @e[type=minecraft:marker,tag=hawaii_origin,limit=1] at @s run function hawaii:internal/step
execute as @e[type=minecraft:marker,tag=hawaii_origin,limit=1] at @s run function hawaii:internal/step
function hawaii:internal/progress

execute if score #i hw >= #total hw as @e[type=minecraft:marker,tag=hawaii_origin,limit=1] at @s run return run function hawaii:internal/finish
schedule function hawaii:internal/tick 1t
