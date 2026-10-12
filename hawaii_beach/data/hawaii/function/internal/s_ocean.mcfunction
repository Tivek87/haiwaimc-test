# 1 rij decoratie: ocean
scoreboard players operation #rz hw = #i hw
scoreboard players operation #rz hw -= #startO hw
scoreboard players operation #rz hw *= #5 hw
scoreboard players operation #rz hw += #gZ hw
data modify storage hawaii:tmp set value {deco:"ocean",hm:"ocean_floor",step:5}
execute store result storage hawaii:tmp rz int 1 run scoreboard players get #rz hw
execute store result storage hawaii:tmp gx int 1 run scoreboard players get #oGX hw
scoreboard players operation #c hw = #ocols hw
function hawaii:grid/row with storage hawaii:tmp
