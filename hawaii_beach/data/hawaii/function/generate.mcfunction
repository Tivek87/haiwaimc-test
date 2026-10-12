# ============================================================
#  HAWAII STRAND GENERATOR  -  Minecraft (NeoForge) 1.21.1
#  Gebruik:   /function hawaii:generate {chunks:4}
#  (of simpel: /function hawaii:beach  of  /function hawaii:beach_1 t/m beach_8)
#  chunks = 1 t/m 8  ->  gebied van (chunks*16) x (chunks*16) blokken
#  Het gebied wordt gecentreerd op de plek waar je staat.
#  Indeling (west -> oost):  zee | strand + tiki bar | jungle | heuvels
# ============================================================

scoreboard objectives add hw dummy
$scoreboard players set #chunks hw $(chunks)
execute if score #chunks hw matches ..0 run scoreboard players set #chunks hw 1
execute if score #chunks hw matches 9.. run scoreboard players set #chunks hw 8

function hawaii:internal/calc
execute align xyz run function hawaii:internal/build with storage hawaii:args
