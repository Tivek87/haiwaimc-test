# Loopt kolom voor kolom (x-richting) door een rij, met een willekeurige verschuiving per vak.
execute store result storage hawaii:tmp jx int 1 run random value 0..3
execute store result storage hawaii:tmp jz int 1 run random value 0..3
function hawaii:grid/cell with storage hawaii:tmp
scoreboard players remove #c hw 1
$execute if score #c hw matches 1.. positioned ~$(step) ~ ~ run function hawaii:grid/cols with storage hawaii:tmp
