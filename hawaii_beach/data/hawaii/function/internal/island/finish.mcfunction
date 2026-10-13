# Klaar (as/at de markering)
function hawaii:gen/island/end
tag @a remove hawaii_builder
bossbar set hawaii:progress color green
bossbar set hawaii:progress name [{"text":"Hawaii eiland: ","color":"gold"},{"text":"klaar! Aloha!","color":"green"}]
tellraw @a [{"text":"[Hawaii] ","color":"gold"},{"text":"Aloha! Het eiland is klaar. Welkom bij Kai's Tiki Bar!","color":"yellow"}]
schedule function hawaii:internal/bar_remove 4s
kill @s
