# Rekent alle grenzen van het gebied uit en zet ze in storage hawaii:args

scoreboard players set #2 hw 2
scoreboard players set #5 hw 5
scoreboard players set #6 hw 6
scoreboard players set #16 hw 16
scoreboard players set #100 hw 100

# grootte en randen (gecentreerd op 0)
scoreboard players operation #size hw = #chunks hw
scoreboard players operation #size hw *= #16 hw
scoreboard players operation #half hw = #size hw
scoreboard players operation #half hw /= #2 hw
scoreboard players set #x0 hw 0
scoreboard players operation #x0 hw -= #half hw
scoreboard players operation #x1 hw = #half hw
scoreboard players remove #x1 hw 1

# zones (percentage van de breedte)
scoreboard players set #pct hw 18
function hawaii:internal/pct
scoreboard players operation #midS hw = #out hw
scoreboard players operation #deepE hw = #out hw
scoreboard players remove #deepE hw 1

scoreboard players set #pct hw 27
function hawaii:internal/pct
scoreboard players operation #shS hw = #out hw
scoreboard players operation #midE hw = #out hw
scoreboard players remove #midE hw 1

scoreboard players set #pct hw 35
function hawaii:internal/pct
scoreboard players operation #bS hw = #out hw
scoreboard players operation #shE hw = #out hw
scoreboard players remove #shE hw 1

scoreboard players set #pct hw 65
function hawaii:internal/pct
scoreboard players operation #jS hw = #out hw

scoreboard players set #pct hw 82
function hawaii:internal/pct
scoreboard players operation #h1 hw = #out hw
scoreboard players set #pct hw 90
function hawaii:internal/pct
scoreboard players operation #h2 hw = #out hw
scoreboard players set #pct hw 96
function hawaii:internal/pct
scoreboard players operation #h3 hw = #out hw

# raster voor decoratie (startpunt, kolommen, rijen)
scoreboard players operation #gZ hw = #x0 hw
scoreboard players add #gZ hw 1

# zee: stap 5
scoreboard players operation #oGX hw = #x0 hw
scoreboard players add #oGX hw 1
scoreboard players operation #ocols hw = #bS hw
scoreboard players operation #ocols hw -= #x0 hw
scoreboard players operation #ocols hw /= #5 hw
scoreboard players operation #orows hw = #size hw
scoreboard players operation #orows hw /= #5 hw

# strand: stap 6
scoreboard players operation #bGX hw = #bS hw
scoreboard players add #bGX hw 1
scoreboard players operation #bcols hw = #jS hw
scoreboard players operation #bcols hw -= #bS hw
scoreboard players operation #bcols hw /= #6 hw
scoreboard players operation #brows hw = #size hw
scoreboard players operation #brows hw /= #6 hw

# jungle: stap 5
scoreboard players operation #jGX hw = #jS hw
scoreboard players add #jGX hw 1
scoreboard players operation #jcols hw = #x1 hw
scoreboard players operation #jcols hw -= #jS hw
scoreboard players add #jcols hw 1
scoreboard players operation #jcols hw /= #5 hw
scoreboard players operation #jrows hw = #size hw
scoreboard players operation #jrows hw /= #5 hw

execute if score #ocols hw matches ..0 run scoreboard players set #ocols hw 1
execute if score #bcols hw matches ..0 run scoreboard players set #bcols hw 1
execute if score #jcols hw matches ..0 run scoreboard players set #jcols hw 1

# naar storage voor de macro's
execute store result storage hawaii:args x0 int 1 run scoreboard players get #x0 hw
execute store result storage hawaii:args x1 int 1 run scoreboard players get #x1 hw
execute store result storage hawaii:args z0 int 1 run scoreboard players get #x0 hw
execute store result storage hawaii:args z1 int 1 run scoreboard players get #x1 hw
execute store result storage hawaii:args deepE int 1 run scoreboard players get #deepE hw
execute store result storage hawaii:args midS int 1 run scoreboard players get #midS hw
execute store result storage hawaii:args midE int 1 run scoreboard players get #midE hw
execute store result storage hawaii:args shS int 1 run scoreboard players get #shS hw
execute store result storage hawaii:args shE int 1 run scoreboard players get #shE hw
execute store result storage hawaii:args jS int 1 run scoreboard players get #jS hw
execute store result storage hawaii:args h1 int 1 run scoreboard players get #h1 hw
execute store result storage hawaii:args h2 int 1 run scoreboard players get #h2 hw
execute store result storage hawaii:args h3 int 1 run scoreboard players get #h3 hw
execute store result storage hawaii:args gZ int 1 run scoreboard players get #gZ hw
execute store result storage hawaii:args oGX int 1 run scoreboard players get #oGX hw
execute store result storage hawaii:args bGX int 1 run scoreboard players get #bGX hw
execute store result storage hawaii:args jGX int 1 run scoreboard players get #jGX hw
