# Zet een markering op de plek van de speler en start het bouwen over meerdere ticks.
kill @e[type=minecraft:marker,tag=hawaii_origin]
kill @e[type=minecraft:marker,tag=hawaii_origin_island]
# oude villagers/dieren/decoratie van een vorige keer weghalen
kill @e[tag=hawaii_ent,distance=..250]
tag @a remove hawaii_builder
tag @s[type=minecraft:player] add hawaii_builder
summon minecraft:marker ~ ~ ~ {Tags:["hawaii_origin"]}

# houd de chunks geladen tijdens het bouwen
function hawaii:internal/force with storage hawaii:args

scoreboard players set #i hw 0
scoreboard players set #loaded hw 0
scoreboard players set #wait hw 0

# voortgangsbalk
bossbar add hawaii:progress "Hawaii strand"
bossbar set hawaii:progress color yellow
bossbar set hawaii:progress style notched_10
execute store result bossbar hawaii:progress max run scoreboard players get #total hw
bossbar set hawaii:progress value 0
bossbar set hawaii:progress name [{"text":"Hawaii strand: ","color":"gold"},{"text":"chunks laden...","color":"yellow"}]
bossbar set hawaii:progress players @a[distance=..256]
bossbar set hawaii:progress visible true

tellraw @a[distance=..256] [{"text":"[Hawaii] ","color":"gold"},{"text":"Bouwen gestart: ","color":"yellow"},{"score":{"name":"#chunks","objective":"hw"},"color":"aqua"},{"text":"x","color":"aqua"},{"score":{"name":"#chunks","objective":"hw"},"color":"aqua"},{"text":" chunks rond je. Even geduld...","color":"yellow"}]
schedule function hawaii:internal/tick 1t
