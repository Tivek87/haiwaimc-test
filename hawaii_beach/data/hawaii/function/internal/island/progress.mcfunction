scoreboard players operation #pct hw = #i hw
scoreboard players operation #pct hw *= #100 hw
scoreboard players operation #pct hw /= #total hw
execute store result bossbar hawaii:progress value run scoreboard players get #i hw
execute if score #wait hw matches 0 run bossbar set hawaii:progress name [{"text":"Hawaii eiland: ","color":"gold"},{"text":"chunk ","color":"yellow"},{"score":{"name":"#i","objective":"hw"},"color":"aqua"},{"text":"/1296  ","color":"aqua"},{"score":{"name":"#pct","objective":"hw"},"color":"white"},{"text":"%","color":"white"}]
execute if score #wait hw matches 1.. run bossbar set hawaii:progress name [{"text":"Hawaii eiland: ","color":"gold"},{"text":"chunks laden... ","color":"yellow"},{"score":{"name":"#i","objective":"hw"},"color":"aqua"},{"text":"/1296  ","color":"aqua"},{"score":{"name":"#pct","objective":"hw"},"color":"white"},{"text":"%","color":"white"}]
