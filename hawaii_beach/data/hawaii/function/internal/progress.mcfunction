# Werkt de voortgangsbalk bij
scoreboard players operation #pct hw = #i hw
scoreboard players operation #pct hw *= #100 hw
scoreboard players operation #pct hw /= #total hw
execute store result bossbar hawaii:progress value run scoreboard players get #i hw
execute if score #i hw matches ..40 run bossbar set hawaii:progress name [{"text":"Hawaii strand: ","color":"gold"},{"text":"gebied leegmaken ","color":"yellow"},{"score":{"name":"#pct","objective":"hw"},"color":"aqua"},{"text":"%","color":"aqua"}]
execute if score #i hw matches 41..48 run bossbar set hawaii:progress name [{"text":"Hawaii strand: ","color":"gold"},{"text":"grond leggen ","color":"yellow"},{"score":{"name":"#pct","objective":"hw"},"color":"aqua"},{"text":"%","color":"aqua"}]
execute if score #i hw matches 49..51 run bossbar set hawaii:progress name [{"text":"Hawaii strand: ","color":"gold"},{"text":"zee, jungle en tiki bar ","color":"yellow"},{"score":{"name":"#pct","objective":"hw"},"color":"aqua"},{"text":"%","color":"aqua"}]
execute if score #i hw >= #startO hw if score #i hw < #endO hw run bossbar set hawaii:progress name [{"text":"Hawaii strand: ","color":"gold"},{"text":"koraal en vissen ","color":"yellow"},{"score":{"name":"#pct","objective":"hw"},"color":"aqua"},{"text":"%","color":"aqua"}]
execute if score #i hw >= #endO hw if score #i hw < #endB hw run bossbar set hawaii:progress name [{"text":"Hawaii strand: ","color":"gold"},{"text":"palmbomen en parasols ","color":"yellow"},{"score":{"name":"#pct","objective":"hw"},"color":"aqua"},{"text":"%","color":"aqua"}]
execute if score #i hw >= #endB hw run bossbar set hawaii:progress name [{"text":"Hawaii strand: ","color":"gold"},{"text":"jungle planten ","color":"yellow"},{"score":{"name":"#pct","objective":"hw"},"color":"aqua"},{"text":"%","color":"aqua"}]
