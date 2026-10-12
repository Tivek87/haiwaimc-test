# Voert 1 bouwstap uit (as/at de markering). #i = huidige stap.
execute if score #i hw >= #total hw run return 0
execute if score #i hw < #nn hw run function hawaii:internal/s_chunk
execute if score #i hw = #nn hw run function hawaii:internal/s_post with storage hawaii:args
scoreboard players add #i hw 1
