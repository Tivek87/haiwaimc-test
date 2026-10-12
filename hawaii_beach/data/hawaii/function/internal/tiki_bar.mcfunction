# Tiki bar, gebouwd rond het midden van het gebied (ingang aan de noordkant)
summon minecraft:marker ~ ~ ~ {Tags:["hawaii_bar"]}
fill ~-6 ~ ~-6 ~6 ~10 ~6 minecraft:air
fill ~-6 ~-1 ~-6 ~6 ~-1 ~6 minecraft:sand replace minecraft:grass_block

# vloer
fill ~-3 ~-1 ~-3 ~3 ~-1 ~3 minecraft:bamboo_mosaic

# hoekpalen
fill ~-3 ~ ~-3 ~-3 ~3 ~-3 minecraft:bamboo_block
fill ~3 ~ ~-3 ~3 ~3 ~-3 minecraft:bamboo_block
fill ~-3 ~ ~3 ~-3 ~3 ~3 minecraft:bamboo_block
fill ~3 ~ ~3 ~3 ~3 ~3 minecraft:bamboo_block

# rieten dak (piramide van hooi)
fill ~-4 ~4 ~-4 ~4 ~4 ~4 minecraft:hay_block
fill ~-3 ~5 ~-3 ~3 ~5 ~3 minecraft:hay_block
fill ~-2 ~6 ~-2 ~2 ~6 ~2 minecraft:hay_block
fill ~-1 ~7 ~-1 ~1 ~7 ~1 minecraft:hay_block
setblock ~ ~8 ~ minecraft:hay_block

# toonbank voorkant + zijkanten
fill ~-2 ~ ~-1 ~2 ~ ~-1 minecraft:stripped_bamboo_block[axis=x]
setblock ~-2 ~ ~ minecraft:stripped_bamboo_block[axis=z]
setblock ~2 ~ ~ minecraft:stripped_bamboo_block[axis=z]
setblock ~-2 ~1 ~-1 minecraft:lantern
setblock ~-1 ~1 ~-1 minecraft:potted_torchflower
setblock ~1 ~1 ~-1 minecraft:yellow_candle[candles=3,lit=true]
setblock ~2 ~1 ~-1 minecraft:potted_bamboo

# achterwand: vaten met drank, bowl met punch, brouwstandaards
fill ~-2 ~ ~3 ~2 ~ ~3 minecraft:barrel[facing=up]
setblock ~-2 ~1 ~3 minecraft:brewing_stand
setblock ~-1 ~1 ~3 minecraft:decorated_pot[facing=north]
setblock ~ ~1 ~3 minecraft:water_cauldron[level=3]
setblock ~2 ~1 ~3 minecraft:brewing_stand
fill ~-2 ~2 ~3 ~2 ~3 ~3 minecraft:bamboo_planks

# hangende lantaarns
setblock ~-1 ~3 ~ minecraft:lantern[hanging=true]
setblock ~1 ~3 ~ minecraft:lantern[hanging=true]

# barkrukken
setblock ~-2 ~ ~-2 minecraft:bamboo_slab[type=bottom]
setblock ~ ~ ~-2 minecraft:bamboo_slab[type=bottom]
setblock ~2 ~ ~-2 minecraft:bamboo_slab[type=bottom]

# tiki fakkels
fill ~-5 ~ ~-5 ~-5 ~1 ~-5 minecraft:bamboo_fence
setblock ~-5 ~2 ~-5 minecraft:torch
fill ~5 ~ ~-5 ~5 ~1 ~-5 minecraft:bamboo_fence
setblock ~5 ~2 ~-5 minecraft:torch
fill ~-5 ~ ~5 ~-5 ~1 ~5 minecraft:bamboo_fence
setblock ~-5 ~2 ~5 minecraft:torch
fill ~5 ~ ~5 ~5 ~1 ~5 minecraft:bamboo_fence
setblock ~5 ~2 ~5 minecraft:torch

# naambord onder de dakrand
setblock ~ ~3 ~-4 minecraft:bamboo_hanging_sign[rotation=8]{front_text:{messages:['""','{"text":"TIKI BAR","color":"gold","bold":true}','{"text":"Aloha!","color":"dark_green"}','""']},back_text:{messages:['""','{"text":"TIKI BAR","color":"gold","bold":true}','{"text":"Aloha!","color":"dark_green"}','""']}}

# barman (villager) met Hawaiiaanse drankjes
kill @e[type=minecraft:villager,tag=hawaii_barman,distance=..12]
kill @e[type=minecraft:parrot,tag=hawaii_bar_parrot,distance=..12]
summon minecraft:villager ~0.5 ~ ~1.5 {Tags:["hawaii_barman"],CustomName:'{"text":"Kai de Tiki Barman","color":"gold"}',CustomNameVisible:1b,NoAI:1b,Invulnerable:1b,PersistenceRequired:1b,Rotation:[180f,0f],VillagerData:{type:"minecraft:jungle",profession:"minecraft:farmer",level:5},Xp:250,Offers:{Recipes:[{buy:{id:"minecraft:emerald",count:1},sell:{id:"minecraft:potion",count:1,components:{"minecraft:custom_name":'{"text":"Pina Colada","color":"yellow","italic":false}',"minecraft:potion_contents":{custom_color:16768256,custom_effects:[{id:"minecraft:regeneration",amplifier:0,duration:200}]}}},maxUses:9999,rewardExp:0b},{buy:{id:"minecraft:emerald",count:1},sell:{id:"minecraft:potion",count:1,components:{"minecraft:custom_name":'{"text":"Blue Hawaii","color":"aqua","italic":false}',"minecraft:potion_contents":{custom_color:2003199,custom_effects:[{id:"minecraft:water_breathing",amplifier:0,duration:3600}]}}},maxUses:9999,rewardExp:0b},{buy:{id:"minecraft:emerald",count:2},sell:{id:"minecraft:potion",count:1,components:{"minecraft:custom_name":'{"text":"Mai Tai","color":"gold","italic":false}',"minecraft:potion_contents":{custom_color:16747520,custom_effects:[{id:"minecraft:speed",amplifier:0,duration:2400},{id:"minecraft:jump_boost",amplifier:0,duration:2400}]}}},maxUses:9999,rewardExp:0b},{buy:{id:"minecraft:emerald",count:1},sell:{id:"minecraft:melon_slice",count:6},maxUses:9999,rewardExp:0b},{buy:{id:"minecraft:cocoa_beans",count:8},sell:{id:"minecraft:emerald",count:1},maxUses:9999,rewardExp:0b}]}}
summon minecraft:parrot ~1.5 ~1 ~3.5 {Tags:["hawaii_bar_parrot"],Variant:0,NoAI:1b,PersistenceRequired:1b,Rotation:[180f,0f]}
