# Rekent de grootte van het gebied uit en zet alles in storage hawaii:args
scoreboard players set #2 hw 2
scoreboard players set #16 hw 16
scoreboard players set #100 hw 100

scoreboard players operation #n hw = #chunks hw
scoreboard players operation #size hw = #chunks hw
scoreboard players operation #size hw *= #16 hw
scoreboard players operation #half hw = #size hw
scoreboard players operation #half hw /= #2 hw
scoreboard players set #x0 hw 0
scoreboard players operation #x0 hw -= #half hw
scoreboard players operation #x1 hw = #half hw
scoreboard players remove #x1 hw 1

# stappen: 1 per chunk + 1 voor details/dieren
scoreboard players operation #nn hw = #n hw
scoreboard players operation #nn hw *= #n hw
scoreboard players operation #total hw = #nn hw
scoreboard players add #total hw 1

execute store result storage hawaii:args n int 1 run scoreboard players get #n hw
execute store result storage hawaii:args size int 1 run scoreboard players get #size hw
execute store result storage hawaii:args x0 int 1 run scoreboard players get #x0 hw
execute store result storage hawaii:args x1 int 1 run scoreboard players get #x1 hw
execute store result storage hawaii:args z0 int 1 run scoreboard players get #x0 hw
execute store result storage hawaii:args z1 int 1 run scoreboard players get #x1 hw
