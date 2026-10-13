# ============================================================
#  HAWAII EILAND  -  36 x 36 chunks (576 x 576 blokken)
#  Gebruik: /function hawaii:island
#  Bouwt een compleet tropisch eiland rond de plek waar je staat:
#  regenwoud, bergen, vulkaan, rivieren met watervallen, kloof,
#  lagune met koraalrif, Polynesisch dorp, koloniaal stadje,
#  plantage, ranch, tempel, vuurtoren, fort en de grote tiki bar.
#  LET OP: vervangt alles in dat gebied. Maak eerst een backup!
# ============================================================
scoreboard objectives add hw dummy
execute align xyz run function hawaii:internal/island/start
