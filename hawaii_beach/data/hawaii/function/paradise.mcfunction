# ============================================================
#  TROPICAL PARADISE  -  /function hawaii:paradise
#  Brengt je naar de Paradise-dimensie: een oneindige wereld met
#  alleen tropische biomen (Moana / Guarma / Tahiti / tiki) die
#  zich vanzelf genereert terwijl je rondloopt.
#  Terug naar je eigen wereld:  /function hawaii:home
#  (werkt pas na het herstarten van de wereld/server)
# ============================================================
function hawaii:load
# terugkeerpunt onthouden (alleen als je in de overworld bent)
execute if dimension minecraft:overworld store result score @s hw_rx run data get entity @s Pos[0]
execute if dimension minecraft:overworld store result score @s hw_ry run data get entity @s Pos[1]
execute if dimension minecraft:overworld store result score @s hw_rz run data get entity @s Pos[2]
execute if dimension minecraft:overworld run scoreboard players set @s hw_saved 1
tellraw @s [{"text":"[Hawaii] ","color":"gold"},{"text":"Op weg naar Paradise... (eerste keer kan even duren)","color":"yellow"}]
execute in hawaii:paradise run spreadplayers 0 0 0 600 false @s
tellraw @s [{"text":"[Hawaii] ","color":"gold"},{"text":"Aloha! Welkom in Paradise. Terug naar huis: ","color":"yellow"},{"text":"/function hawaii:home","color":"aqua"}]
