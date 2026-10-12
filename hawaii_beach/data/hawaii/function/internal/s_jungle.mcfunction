# 1 rij decoratie: jungle
scoreboard players operation #rz hw = #i hw
scoreboard players operation #rz hw -= #endB hw
scoreboard players operation #rz hw *= #5 hw
scoreboard players operation #rz hw += #gZ hw
data modify storage hawaii:tmp set value {deco:"jungle",hm:"motion_blocking_no_leaves",step:5}
execute store result storage hawaii:tmp rz int 1 run scoreboard players get #rz hw
execute store result storage hawaii:tmp gx int 1 run scoreboard players get #jGX hw
scoreboard players operation #c hw = #jcols hw
function hawaii:grid/row with storage hawaii:tmp
