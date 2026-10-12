# Uitgevoerd op het gras (jungle + heuvels)
execute unless block ~ ~-1 ~ minecraft:grass_block run return 0
execute if entity @e[type=minecraft:marker,tag=hawaii_bar,distance=..8] run return 0
execute store result score #rand hw run random value 1..100
execute if score #rand hw matches 1..22 run place feature minecraft:jungle_tree ~ ~ ~
execute if score #rand hw matches 23..32 run place feature minecraft:mega_jungle_tree ~ ~ ~
execute if score #rand hw matches 33..48 run place feature minecraft:jungle_bush ~ ~ ~
execute if score #rand hw matches 49..60 run place feature minecraft:bamboo_some_podzol ~ ~ ~
execute if score #rand hw matches 61..66 run function hawaii:deco/palm
execute if score #rand hw matches 67..74 run place feature minecraft:patch_melon ~ ~ ~
execute if score #rand hw matches 75..84 run place feature minecraft:flower_default ~ ~ ~
execute if score #rand hw matches 85..88 run summon minecraft:parrot ~0.5 ~1 ~0.5
execute if score #rand hw matches 89..90 run summon minecraft:ocelot ~0.5 ~ ~0.5
# extra gras/varens tussen alles door
execute store result score #rand hw run random value 1..100
execute if score #rand hw matches 1..60 run place feature minecraft:patch_grass_jungle ~ ~ ~
