# Start het bouwen van het eiland (as/at de speler, afgerond op een blok)
kill @e[type=minecraft:marker,tag=hawaii_origin]
kill @e[type=minecraft:marker,tag=hawaii_origin_island]
kill @e[tag=hawaii_ent,distance=..400]
tag @a remove hawaii_builder
tag @s[type=minecraft:player] add hawaii_builder
summon minecraft:marker ~ ~ ~ {Tags:["hawaii_origin_island"]}

scoreboard players set #i hw 0
scoreboard players set #total hw 1296
scoreboard players set #n hw 36
scoreboard players set #16 hw 16
scoreboard players set #100 hw 100
scoreboard players set #x0 hw -288
scoreboard players set #wait hw 0

# eerste chunks alvast laden
function hawaii:gen/island/start

bossbar add hawaii:progress "Hawaii eiland"
bossbar set hawaii:progress color yellow
bossbar set hawaii:progress style notched_20
bossbar set hawaii:progress max 1296
bossbar set hawaii:progress value 0
bossbar set hawaii:progress name [{"text":"Hawaii eiland: ","color":"gold"},{"text":"chunks laden...","color":"yellow"}]
bossbar set hawaii:progress players @a
bossbar set hawaii:progress visible true

tellraw @a [{"text":"[Hawaii] ","color":"gold"},{"text":"Het eiland wordt gebouwd: 36x36 chunks (576x576 blokken). Dit duurt een paar minuten, blijf in de buurt.","color":"yellow"}]
schedule function hawaii:internal/island/tick 1t
