# Terug uit Paradise naar de plek waar je vandaan kwam (of naar het midden van de overworld)
function hawaii:load
execute if score @s hw_saved matches 1 run return run function hawaii:internal/paradise/home_saved
execute in minecraft:overworld run spreadplayers 0 0 0 16 false @s
