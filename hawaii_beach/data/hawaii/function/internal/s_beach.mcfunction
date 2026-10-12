# 1 rij decoratie: beach
scoreboard players operation #rz hw = #i hw
scoreboard players operation #rz hw -= #endO hw
scoreboard players operation #rz hw *= #6 hw
scoreboard players operation #rz hw += #gZ hw
data modify storage hawaii:tmp set value {deco:"beach",hm:"motion_blocking_no_leaves",step:6}
execute store result storage hawaii:tmp rz int 1 run scoreboard players get #rz hw
execute store result storage hawaii:tmp gx int 1 run scoreboard players get #bGX hw
scoreboard players operation #c hw = #bcols hw
function hawaii:grid/row with storage hawaii:tmp
