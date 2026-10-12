# Voert 1 bouwstap uit (as/at de markering). #i = huidige stap.
execute if score #i hw >= #total hw run return 0
execute if score #i hw matches 0..40 run function hawaii:internal/s_clear
execute if score #i hw matches 41..48 run function hawaii:internal/s_ground
execute if score #i hw matches 49 run function hawaii:internal/s_water with storage hawaii:args
execute if score #i hw matches 50 run function hawaii:internal/s_land with storage hawaii:args
execute if score #i hw matches 51 run function hawaii:internal/tiki_bar
execute if score #i hw >= #startO hw if score #i hw < #endO hw run function hawaii:internal/s_ocean
execute if score #i hw >= #endO hw if score #i hw < #endB hw run function hawaii:internal/s_beach
execute if score #i hw >= #endB hw if score #i hw < #total hw run function hawaii:internal/s_jungle
scoreboard players add #i hw 1
