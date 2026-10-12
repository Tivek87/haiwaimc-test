# Loopt rij voor rij (z-richting) door een zone. Gebruikt #r (rijen) en #cols (kolommen).
scoreboard players operation #c hw = #cols hw
function hawaii:grid/cols with storage hawaii:tmp
scoreboard players remove #r hw 1
$execute if score #r hw matches 1.. positioned ~ ~ ~$(step) run function hawaii:grid/rows with storage hawaii:tmp
