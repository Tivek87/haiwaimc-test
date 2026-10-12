# Werkt de voortgangsbalk bij
scoreboard players operation #pct hw = #i hw
scoreboard players operation #pct hw *= #100 hw
scoreboard players operation #pct hw /= #total hw
execute store result bossbar hawaii:progress value run scoreboard players get #i hw
execute if score #i hw < #nn hw run bossbar set hawaii:progress name [{"text":"Hawaii strand: ","color":"gold"},{"text":"terrein en gebouwen ","color":"yellow"},{"score":{"name":"#i","objective":"hw"},"color":"aqua"},{"text":"/","color":"aqua"},{"score":{"name":"#nn","objective":"hw"},"color":"aqua"},{"text":" chunks  ","color":"aqua"},{"score":{"name":"#pct","objective":"hw"},"color":"white"},{"text":"%","color":"white"}]
execute if score #i hw >= #nn hw run bossbar set hawaii:progress name [{"text":"Hawaii strand: ","color":"gold"},{"text":"dieren, villagers en details ","color":"yellow"},{"score":{"name":"#pct","objective":"hw"},"color":"white"},{"text":"%","color":"white"}]
