# Haalt de voortgangsbalk weg (niet als er alweer iets gebouwd wordt)
execute unless entity @e[type=minecraft:marker,tag=hawaii_origin] unless entity @e[type=minecraft:marker,tag=hawaii_origin_island] run bossbar remove hawaii:progress
