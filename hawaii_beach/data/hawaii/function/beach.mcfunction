# Snelle start zonder argumenten: bouwt een strand van 4 x 4 chunks.
# Andere grootte: /function hawaii:beach_1 t/m hawaii:beach_8
# of: /function hawaii:generate {chunks:N}
tellraw @s [{"text":"[Hawaii] ","color":"gold"},{"text":"Standaard 4x4 chunks. Andere grootte: ","color":"gray"},{"text":"/function hawaii:beach_1","color":"aqua"},{"text":" t/m ","color":"gray"},{"text":"beach_8","color":"aqua"}]
function hawaii:generate {chunks:4}
