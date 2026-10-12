# Maakt 1 chunk leeg en plaatst de gegenereerde structuur + biomen (zee = warm_ocean, strand, jungle)
$fill ~$(px) ~-12 ~$(pz) ~$(px2) ~56 ~$(pz2) minecraft:air
$place template hawaii:s$(n)/c_$(cx)_$(cz) ~$(px) ~-12 ~$(pz)
$function hawaii:gen/s$(n)/b_$(cx)_$(cz)
