# Klaar (as/at de markering)
function hawaii:internal/unforce with storage hawaii:args
tag @a remove hawaii_builder

bossbar set hawaii:progress color green
bossbar set hawaii:progress name [{"text":"Hawaii strand: ","color":"gold"},{"text":"klaar! Aloha!","color":"green"}]
tellraw @a[distance=..256] [{"text":"[Hawaii] ","color":"gold"},{"text":"Aloha! Strand klaar: ","color":"yellow"},{"score":{"name":"#chunks","objective":"hw"},"color":"aqua"},{"text":"x","color":"aqua"},{"score":{"name":"#chunks","objective":"hw"},"color":"aqua"},{"text":" chunks","color":"aqua"}]
schedule function hawaii:internal/bar_remove 3s
kill @s
