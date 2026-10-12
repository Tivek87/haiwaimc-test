# Uitgevoerd op het zand (blok boven de grond)
execute unless block ~ ~-1 ~ minecraft:sand run return 0
execute if entity @e[type=minecraft:marker,tag=hawaii_bar,distance=..9] run return 0
execute store result score #rand hw run random value 1..100
execute if score #rand hw matches 1..35 run function hawaii:deco/palm
execute if score #rand hw matches 36..50 run function hawaii:deco/palm_lean
execute if score #rand hw matches 51..58 run function hawaii:deco/umbrella
execute if score #rand hw matches 59..63 run summon minecraft:turtle ~0.5 ~ ~0.5
