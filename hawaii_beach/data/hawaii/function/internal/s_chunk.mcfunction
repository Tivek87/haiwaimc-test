# Bouwt chunk nummer #i: cx = i % n, cz = i / n
scoreboard players operation #cx hw = #i hw
scoreboard players operation #cx hw %= #n hw
scoreboard players operation #cz hw = #i hw
scoreboard players operation #cz hw /= #n hw
scoreboard players operation #px hw = #cx hw
scoreboard players operation #px hw *= #16 hw
scoreboard players operation #px hw += #x0 hw
scoreboard players operation #pz hw = #cz hw
scoreboard players operation #pz hw *= #16 hw
scoreboard players operation #pz hw += #x0 hw
execute store result storage hawaii:args cx int 1 run scoreboard players get #cx hw
execute store result storage hawaii:args cz int 1 run scoreboard players get #cz hw
execute store result storage hawaii:args px int 1 run scoreboard players get #px hw
execute store result storage hawaii:args pz int 1 run scoreboard players get #pz hw
scoreboard players add #px hw 15
scoreboard players add #pz hw 15
execute store result storage hawaii:args px2 int 1 run scoreboard players get #px hw
execute store result storage hawaii:args pz2 int 1 run scoreboard players get #pz hw
function hawaii:internal/chunk with storage hawaii:args
