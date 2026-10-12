# Uitgevoerd in het water net boven de zeebodem
execute unless block ~ ~ ~ minecraft:water run return 0
execute store result score #rand hw run random value 1..100
execute if score #rand hw matches 1..30 if block ~ ~3 ~ minecraft:water run place feature minecraft:warm_ocean_vegetation ~ ~ ~
execute if score #rand hw matches 31..55 run place feature minecraft:seagrass_tall ~ ~ ~
execute if score #rand hw matches 56..65 run place feature minecraft:sea_pickle ~ ~ ~
execute if score #rand hw matches 66..72 if block ~ ~3 ~ minecraft:water run place feature minecraft:kelp ~ ~ ~
execute if score #rand hw matches 73..85 if block ~ ~1 ~ minecraft:water run summon minecraft:tropical_fish ~0.5 ~1 ~0.5
