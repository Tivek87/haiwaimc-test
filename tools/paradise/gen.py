"""Genereert het 'Tropical Paradise' worldgen-pakket: eigen biomen, bomen, watervallen, ruines en een dimensie.

- data/hawaii/worldgen/...           eigen biomen, features, structuren
- data/hawaii/dimension/paradise     een hele wereld van tropische biomen (vanilla terrein)
- data/minecraft/worldgen/biome/...  vanilla jungle/bamboo/sparse jungle/warm ocean worden tropisch (ook in je
                                     bestaande wereld, in nieuwe chunks)
"""
import copy
import gzip
import json
import pathlib
import re

from generate import MCDATA
from world import parse_state, st

from .ruins import RUINS

HERE = pathlib.Path(__file__).resolve().parent.parent
VAN = HERE / "vanilla_1.21.1"
REG = json.loads((VAN / "registries.json").read_text())
VBIOMES = json.loads(gzip.open(VAN / "biomes.json.gz", "rt").read())
VNOISE = json.loads(gzip.open(VAN / "noise_settings_overworld.json.gz", "rt").read())
VDIM = json.loads(gzip.open(VAN / "dimension_overworld.json.gz", "rt").read())
VPRESET = json.loads((VAN / "world_preset_normal.json").read_text())

H = "hawaii:"


def bs(state):
    """'minecraft:x[a=b]' -> {"Name": ..., "Properties": {...}} voor in JSON."""
    name, props = parse_state(st(state) if "[" not in state and ":" not in state else state)
    d = {"Name": name}
    if props:
        d["Properties"] = props
    return d


def leaves(name, persistent="false"):
    return {"Name": f"minecraft:{name}", "Properties": {"distance": "7", "persistent": persistent, "waterlogged": "false"}}


def simple(state):
    return {"type": "minecraft:simple_state_provider", "state": state}


def weighted(entries):
    return {"type": "minecraft:weighted_state_provider", "entries": [{"data": d, "weight": w} for d, w in entries]}


def uniform(a, b):
    return {"type": "minecraft:uniform", "min_inclusive": a, "max_inclusive": b}


def tree(trunk, foliage, log, leaf_provider, decorators=(), dirt="minecraft:dirt", force_dirt=False,
         size=(1, 0, 1), ignore_vines=True):
    return {"type": "minecraft:tree", "config": {
        "decorators": list(decorators),
        "dirt_provider": simple({"Name": dirt}),
        "foliage_placer": foliage,
        "foliage_provider": leaf_provider,
        "force_dirt": force_dirt,
        "ignore_vines": ignore_vines,
        "minimum_size": {"type": "minecraft:two_layers_feature_size", "limit": size[0], "lower_size": size[1],
                         "upper_size": size[2]},
        "trunk_placer": trunk,
        "trunk_provider": simple({"Name": f"minecraft:{log}", "Properties": {"axis": "y"}}),
    }}


# ===================================================================== bomen en planten
COCOA = {"type": "minecraft:cocoa", "probability": 0.3}
TRUNK_VINE = {"type": "minecraft:trunk_vine"}


def leave_vine(p):
    return {"type": "minecraft:leave_vine", "probability": p}


CONFIGURED = {
    # kokospalm: gebogen stam, hangende 'cherry'-kroon met jungle-bladeren, kokosnoten (cacao)
    "palm": tree({"type": "minecraft:bending_trunk_placer", "base_height": 7, "height_rand_a": 3, "height_rand_b": 0,
                  "min_height_for_leaves": 7, "bend_length": uniform(1, 3)},
                 {"type": "minecraft:cherry_foliage_placer", "radius": 3, "offset": 0, "height": 3,
                  "wide_bottom_layer_hole_chance": 0.6, "corner_hole_chance": 0.9, "hanging_leaves_chance": 0.6,
                  "hanging_leaves_extension_chance": 0.5},
                 "jungle_log", simple(leaves("jungle_leaves")), [{"type": "minecraft:cocoa", "probability": 0.8}],
                 dirt="minecraft:sand", size=(1, 0, 1)),
    "palm_tall": tree({"type": "minecraft:bending_trunk_placer", "base_height": 10, "height_rand_a": 4, "height_rand_b": 0,
                       "min_height_for_leaves": 10, "bend_length": uniform(2, 4)},
                      {"type": "minecraft:cherry_foliage_placer", "radius": 4, "offset": 0, "height": 3,
                       "wide_bottom_layer_hole_chance": 0.7, "corner_hole_chance": 0.9, "hanging_leaves_chance": 0.7,
                       "hanging_leaves_extension_chance": 0.6},
                      "jungle_log", simple(leaves("jungle_leaves")), [{"type": "minecraft:cocoa", "probability": 0.9}],
                      dirt="minecraft:sand", size=(1, 0, 1)),
    # reuzenboom van het regenwoud
    "giant_tree": tree({"type": "minecraft:mega_jungle_trunk_placer", "base_height": 22, "height_rand_a": 6, "height_rand_b": 12},
                       {"type": "minecraft:jungle_foliage_placer", "radius": 3, "offset": 0, "height": 3},
                       "jungle_log", simple(leaves("jungle_leaves")), [TRUNK_VINE, leave_vine(0.4), COCOA],
                       size=(1, 1, 2), ignore_vines=False),
    # gewone hoge regenwoudboom
    "rain_tree": tree({"type": "minecraft:straight_trunk_placer", "base_height": 9, "height_rand_a": 6, "height_rand_b": 0},
                      {"type": "minecraft:blob_foliage_placer", "radius": 3, "offset": 0, "height": 3},
                      "jungle_log", simple(leaves("jungle_leaves")), [COCOA, TRUNK_VINE, leave_vine(0.35)]),
    # brede schaduwboom (monkeypod / banyan-gevoel)
    "shade_tree": tree({"type": "minecraft:fancy_trunk_placer", "base_height": 8, "height_rand_a": 6, "height_rand_b": 0},
                       {"type": "minecraft:fancy_foliage_placer", "radius": 3, "offset": 4, "height": 4},
                       "jungle_log", simple(leaves("jungle_leaves")), [leave_vine(0.3)], size=(0, 0, 0)),
    # roze bloeiende boom
    "monkeypod": tree({"type": "minecraft:cherry_trunk_placer", "base_height": 6, "height_rand_a": 2, "height_rand_b": 0,
                       "branch_count": {"type": "minecraft:weighted_list", "distribution": [{"data": 2, "weight": 1}, {"data": 3, "weight": 1}]},
                       "branch_end_offset_from_top": uniform(-1, 0), "branch_horizontal_length": uniform(3, 5),
                       "branch_start_offset_from_top": {"min_inclusive": -4, "max_inclusive": -3}},
                      {"type": "minecraft:cherry_foliage_placer", "radius": 5, "offset": 0, "height": 4,
                       "wide_bottom_layer_hole_chance": 0.25, "corner_hole_chance": 0.25, "hanging_leaves_chance": 0.2,
                       "hanging_leaves_extension_chance": 0.3},
                      "dark_oak_log", simple(leaves("cherry_leaves")), [], size=(1, 0, 2)),
    # plumeria (frangipani): witte/roze bloesem
    "plumeria": tree({"type": "minecraft:cherry_trunk_placer", "base_height": 4, "height_rand_a": 1, "height_rand_b": 0,
                      "branch_count": {"type": "minecraft:weighted_list", "distribution": [{"data": 1, "weight": 1}, {"data": 2, "weight": 1}]},
                      "branch_end_offset_from_top": uniform(-1, 0), "branch_horizontal_length": uniform(2, 3),
                      "branch_start_offset_from_top": {"min_inclusive": -3, "max_inclusive": -2}},
                     {"type": "minecraft:cherry_foliage_placer", "radius": 3, "offset": 0, "height": 3,
                      "wide_bottom_layer_hole_chance": 0.3, "corner_hole_chance": 0.4, "hanging_leaves_chance": 0.1,
                      "hanging_leaves_extension_chance": 0.1},
                     "stripped_birch_log", weighted([(leaves("flowering_azalea_leaves"), 3), (leaves("azalea_leaves"), 1)]),
                     [], size=(1, 0, 2)),
    # boomvaren (hapu'u) van het nevelwoud
    "tree_fern": tree({"type": "minecraft:straight_trunk_placer", "base_height": 3, "height_rand_a": 2, "height_rand_b": 0},
                      {"type": "minecraft:acacia_foliage_placer", "radius": 2, "offset": 0},
                      "spruce_log", simple(leaves("azalea_leaves")), [leave_vine(0.15)]),
    # koa (acacia-achtig) voor de hooglanden
    "koa": tree({"type": "minecraft:forking_trunk_placer", "base_height": 5, "height_rand_a": 2, "height_rand_b": 2},
                {"type": "minecraft:acacia_foliage_placer", "radius": 3, "offset": 0},
                "acacia_log", simple(leaves("jungle_leaves")), [], size=(1, 0, 2)),
    # dichte varens en gras
    "ferns_dense": {"type": "minecraft:random_patch", "config": {
        "feature": {"feature": {"type": "minecraft:simple_block", "config": {"to_place": weighted([
            ({"Name": "minecraft:fern"}, 4), ({"Name": "minecraft:large_fern"}, 2), ({"Name": "minecraft:short_grass"}, 2),
            ({"Name": "minecraft:tall_grass"}, 1)])}},
            "placement": [{"type": "minecraft:block_predicate_filter", "predicate": {"type": "minecraft:matching_blocks", "blocks": "minecraft:air"}}]},
        "tries": 48, "xz_spread": 7, "y_spread": 3}},
    # tropische bloemen
    "flowers_tropical": {"type": "minecraft:random_patch", "config": {
        "feature": {"feature": {"type": "minecraft:simple_block", "config": {"to_place": weighted([
            ({"Name": "minecraft:red_tulip"}, 3), ({"Name": "minecraft:orange_tulip"}, 3), ({"Name": "minecraft:pink_tulip"}, 3),
            ({"Name": "minecraft:allium"}, 2), ({"Name": "minecraft:blue_orchid"}, 2), ({"Name": "minecraft:torchflower"}, 2),
            ({"Name": "minecraft:poppy"}, 1), ({"Name": "minecraft:rose_bush"}, 2), ({"Name": "minecraft:peony"}, 1),
            ({"Name": "minecraft:pitcher_plant"}, 1)])}},
            "placement": [{"type": "minecraft:block_predicate_filter", "predicate": {"type": "minecraft:matching_blocks", "blocks": "minecraft:air"}}]},
        "tries": 40, "xz_spread": 6, "y_spread": 2}},
    # watervallen uit kliffen en bergwanden
    "waterfall": {"type": "minecraft:spring_feature", "config": {
        "hole_count": 1, "requires_block_below": True, "rock_count": 4,
        "state": {"Name": "minecraft:water", "Properties": {"falling": "true"}},
        "valid_blocks": ["minecraft:stone", "minecraft:andesite", "minecraft:tuff", "minecraft:dirt", "minecraft:moss_block",
                         "minecraft:mossy_cobblestone", "minecraft:grass_block", "minecraft:granite", "minecraft:diorite",
                         "minecraft:calcite", "minecraft:terracotta"]}},
}


def checked(feature, on=("minecraft:grass_block", "minecraft:dirt", "minecraft:podzol", "minecraft:coarse_dirt",
                         "minecraft:moss_block", "minecraft:rooted_dirt", "minecraft:mud")):
    return {"feature": feature, "placement": [{"type": "minecraft:block_predicate_filter", "predicate": {
        "type": "minecraft:all_of", "predicates": [
            {"type": "minecraft:matching_blocks", "offset": [0, -1, 0], "blocks": list(on)},
            {"type": "minecraft:any_of", "predicates": [
                {"type": "minecraft:matching_blocks", "blocks": "minecraft:air"},
                {"type": "minecraft:matching_block_tag", "tag": "minecraft:replaceable_by_trees"}]}]}}]}


SANDY = ("minecraft:sand", "minecraft:grass_block", "minecraft:dirt", "minecraft:coarse_dirt", "minecraft:podzol",
         "minecraft:black_concrete_powder")
PLACED_TREES = {
    "palm_checked": checked(H + "palm", SANDY),
    "palm_tall_checked": checked(H + "palm_tall", SANDY),
    "giant_tree_checked": checked(H + "giant_tree"),
    "rain_tree_checked": checked(H + "rain_tree"),
    "shade_tree_checked": checked(H + "shade_tree"),
    "monkeypod_checked": checked(H + "monkeypod"),
    "plumeria_checked": checked(H + "plumeria"),
    "tree_fern_checked": checked(H + "tree_fern"),
    "koa_checked": checked(H + "koa"),
}


def selector(default, items):
    return {"type": "minecraft:random_selector", "config": {"default": default,
                                                            "features": [{"chance": c, "feature": f} for f, c in items]}}


SELECTORS = {
    "trees_rainforest": selector(H + "rain_tree_checked", [(H + "giant_tree_checked", 0.14), ("minecraft:jungle_bush", 0.4),
                                                           (H + "shade_tree_checked", 0.06), (H + "palm_checked", 0.05),
                                                           (H + "plumeria_checked", 0.03)]),
    "trees_lost": selector(H + "giant_tree_checked", [(H + "rain_tree_checked", 0.35), ("minecraft:jungle_bush", 0.35)]),
    "trees_bamboo": selector("minecraft:jungle_bush", [(H + "rain_tree_checked", 0.25), (H + "palm_checked", 0.1)]),
    "trees_grove": selector(H + "palm_checked", [(H + "palm_tall_checked", 0.35), (H + "plumeria_checked", 0.12),
                                                 ("minecraft:jungle_bush", 0.15), (H + "monkeypod_checked", 0.05)]),
    "trees_plumeria": selector(H + "plumeria_checked", [(H + "monkeypod_checked", 0.3), (H + "palm_checked", 0.15),
                                                        ("minecraft:jungle_bush", 0.15)]),
    "trees_fields": selector(H + "palm_tall_checked", [(H + "monkeypod_checked", 0.3), (H + "shade_tree_checked", 0.15),
                                                       (H + "palm_checked", 0.3)]),
    "trees_highlands": selector(H + "koa_checked", [(H + "shade_tree_checked", 0.15), ("minecraft:jungle_bush", 0.2),
                                                    (H + "palm_checked", 0.08)]),
    "trees_cloud": selector(H + "tree_fern_checked", [(H + "rain_tree_checked", 0.25), ("minecraft:jungle_bush", 0.25),
                                                      (H + "giant_tree_checked", 0.05)]),
    "trees_peaks": selector("minecraft:jungle_bush", [(H + "tree_fern_checked", 0.45), (H + "rain_tree_checked", 0.15)]),
    "trees_canyon": selector(H + "koa_checked", [(H + "palm_checked", 0.3)]),
    "trees_beach": selector(H + "palm_checked", [(H + "palm_tall_checked", 0.45)]),
    "trees_river": selector(H + "palm_checked", [(H + "rain_tree_checked", 0.4), ("minecraft:jungle_bush", 0.3)]),
}


def veg(feature, count, extra=0, water_depth=0, heightmap="OCEAN_FLOOR"):
    c = count if not extra else {"type": "minecraft:weighted_list", "distribution": [
        {"data": count, "weight": 9}, {"data": count + extra, "weight": 1}]}
    return {"feature": feature, "placement": [
        {"type": "minecraft:count", "count": c}, {"type": "minecraft:in_square"},
        {"type": "minecraft:surface_water_depth_filter", "max_water_depth": water_depth},
        {"type": "minecraft:heightmap", "heightmap": heightmap}, {"type": "minecraft:biome"}]}


def patch(feature, rarity_or_count, kind="count"):
    first = {"type": "minecraft:count", "count": rarity_or_count} if kind == "count" else \
        {"type": "minecraft:rarity_filter", "chance": rarity_or_count}
    return {"feature": feature, "placement": [first, {"type": "minecraft:in_square"},
                                              {"type": "minecraft:heightmap", "heightmap": "MOTION_BLOCKING"},
                                              {"type": "minecraft:biome"}]}


def springs(count, lo=66, hi=250):
    return {"feature": H + "waterfall", "placement": [
        {"type": "minecraft:count", "count": count}, {"type": "minecraft:in_square"},
        {"type": "minecraft:height_range", "height": {"type": "minecraft:uniform", "min_inclusive": {"absolute": lo},
                                                      "max_inclusive": {"absolute": hi}}},
        {"type": "minecraft:biome"}]}


PLACED = dict(PLACED_TREES)
PLACED.update({
    "trees_rainforest": veg(H + "trees_rainforest", 34, 3),
    "trees_lost": veg(H + "trees_lost", 30, 4),
    "trees_bamboo": veg(H + "trees_bamboo", 8, 2),
    "trees_grove": veg(H + "trees_grove", 3, 2),
    "trees_plumeria": veg(H + "trees_plumeria", 6, 2),
    "trees_fields": veg(H + "trees_fields", 1, 2),
    "trees_highlands": veg(H + "trees_highlands", 2, 2),
    "trees_cloud": veg(H + "trees_cloud", 14, 3),
    "trees_peaks": veg(H + "trees_peaks", 4, 2),
    "trees_canyon": veg(H + "trees_canyon", 0, 2),
    "trees_beach": veg(H + "trees_beach", 1, 3),
    "trees_motu": veg(H + "trees_beach", 4, 2),
    "trees_river": veg(H + "trees_river", 1, 2),
    "ferns_dense": patch(H + "ferns_dense", 5),
    "ferns_light": patch(H + "ferns_dense", 2),
    "flowers_tropical": patch(H + "flowers_tropical", 3),
    "flowers_light": patch(H + "flowers_tropical", 4, "rarity"),
    "waterfalls_peaks": springs(60),
    "waterfalls_hills": springs(18),
})
# globale volgorde van eigen features per stap (voorkomt 'feature order cycle')
HAWAII_ORDER = {
    8: ["waterfalls_peaks", "waterfalls_hills"],
    9: ["trees_rainforest", "trees_lost", "trees_bamboo", "trees_grove", "trees_plumeria", "trees_fields",
        "trees_highlands", "trees_cloud", "trees_peaks", "trees_canyon", "trees_beach", "trees_motu", "trees_river",
        "ferns_dense", "ferns_light", "flowers_tropical", "flowers_light"],
}


# ===================================================================== biomen
def c(h):
    return int(h.lstrip("#"), 16)


# base: vanilla biome waarvan ondergrond-features/carvers/spawns komen; veg: extra vanilla vegetatie; hw: eigen features
BIOMES = {
    "tropical_rainforest": dict(base="jungle", grass="#3fc32a", foliage="#2fa82a", water="#3fd1e8", wfog="#2a9fb5",
                                sky="#79b4ff", fog="#c4e2ee", particle=("minecraft:spore_blossom_air", 0.0025),
                                music="minecraft:music.overworld.jungle",
                                veg=["glow_lichen", "bamboo_light", "patch_grass_jungle", "flower_warm", "brown_mushroom_normal",
                                     "red_mushroom_normal", "patch_sugar_cane", "vines", "patch_melon"],
                                hw={8: ["waterfalls_hills"], 9: ["trees_rainforest", "ferns_dense", "flowers_light"]}),
    "lost_jungle": dict(base="jungle", grass="#36a82a", foliage="#24902a", water="#2fb8b0", wfog="#1d7f7a",
                        sky="#6fa0d8", fog="#9ec7b8", particle=("minecraft:spore_blossom_air", 0.006),
                        music="minecraft:music.overworld.jungle",
                        veg=["glow_lichen", "patch_grass_jungle", "brown_mushroom_normal", "red_mushroom_normal", "vines"],
                        hw={8: ["waterfalls_hills"], 9: ["trees_lost", "ferns_dense"]}),
    "bamboo_valley": dict(base="bamboo_jungle", grass="#6ad63a", foliage="#58c83a", water="#3fd1e8", wfog="#2a9fb5",
                          sky="#79b4ff", fog="#c7e6d8", particle=("minecraft:spore_blossom_air", 0.0015),
                          music="minecraft:music.overworld.bamboo_jungle",
                          veg=["glow_lichen", "bamboo", "patch_grass_jungle", "flower_warm", "patch_sugar_cane", "vines", "patch_melon"],
                          hw={9: ["trees_bamboo", "ferns_light", "flowers_light"]}),
    "tiki_grove": dict(base="sparse_jungle", grass="#6fd848", foliage="#4fc040", water="#2fe3d4", wfog="#21b8bf",
                       sky="#6db7ff", fog="#d2ecff", particle=("minecraft:cherry_leaves", 0.0015),
                       music="minecraft:music.overworld.cherry_grove",
                       veg=["glow_lichen", "patch_grass_jungle", "flower_warm", "patch_sugar_cane", "vines", "patch_melon"],
                       hw={9: ["trees_grove", "ferns_light", "flowers_tropical"]}),
    "plumeria_valley": dict(base="cherry_grove", grass="#7fdc54", foliage="#5ccc48", water="#2fe3d4", wfog="#21b8bf",
                            sky="#6db7ff", fog="#ffe6f0", particle=("minecraft:cherry_leaves", 0.004),
                            music="minecraft:music.overworld.cherry_grove",
                            veg=["flower_cherry", "patch_tall_grass_2", "patch_grass_plain", "flower_plains"],
                            hw={9: ["trees_plumeria", "flowers_tropical"]}),
    "guarma_fields": dict(base="plains", grass="#9ccf5a", foliage="#7cbf4a", water="#2fd8d0", wfog="#21b0b8",
                          sky="#74b6ff", fog="#ffe9cf", particle=None, music="minecraft:music.overworld.meadow",
                          veg=["patch_tall_grass_2", "patch_sugar_cane", "patch_grass_plain", "flower_plains", "patch_melon"],
                          hw={9: ["trees_fields", "flowers_light"]}),
    "guarma_highlands": dict(base="savanna_plateau", grass="#a8b85a", foliage="#8ca84a", water="#2fd8d0", wfog="#21b0b8",
                             sky="#7ab4ff", fog="#f2e0c0", particle=None, music="minecraft:music.overworld.badlands",
                             veg=["patch_tall_grass", "patch_grass_savanna", "flower_default"],
                             hw={8: ["waterfalls_hills"], 9: ["trees_highlands", "flowers_light"]}),
    "moorea_peaks": dict(base="jagged_peaks", grass="#45b83a", foliage="#33a034", water="#3fc8e0", wfog="#2a8fa5",
                         sky="#7fb8ff", fog="#e2ecf2", particle=("minecraft:white_ash", 0.003),
                         music="minecraft:music.overworld.jagged_peaks",
                         veg=["glow_lichen", "vines"],
                         hw={8: ["waterfalls_peaks"], 9: ["trees_peaks", "ferns_dense"]}),
    "cloud_forest": dict(base="old_growth_spruce_taiga", grass="#4fb06a", foliage="#3a9e5a", water="#3fc8e0",
                         wfog="#2a8fa5", sky="#8cb8e8", fog="#e2ecf2", particle=("minecraft:white_ash", 0.005),
                         music="minecraft:music.overworld.old_growth_taiga",
                         veg=["glow_lichen", "patch_large_fern", "patch_grass_taiga", "brown_mushroom_old_growth",
                              "red_mushroom_old_growth", "vines"],
                         hw={8: ["waterfalls_hills"], 9: ["trees_cloud", "ferns_dense"]}),
    "red_canyon": dict(base="badlands", grass="#b9a65b", foliage="#9e8f4a", water="#47c3d6", wfog="#2c8fa0",
                       sky="#8fb4ff", fog="#f0c9a0", particle=None, music="minecraft:music.overworld.badlands",
                       veg=["patch_grass_badlands", "patch_dead_bush_badlands", "patch_sugar_cane_badlands"],
                       hw={8: ["waterfalls_hills"], 9: ["trees_canyon"]}),
    "mangrove_coast": dict(base="mangrove_swamp", grass="#4cc046", foliage="#3aa83a", water="#3fc0b8", wfog="#2a8f8a",
                           sky="#79b4ff", fog="#c7e6d8", particle=None, music="minecraft:music.overworld.swamp",
                           veg=None, hw={9: ["flowers_light"]}),
    "white_sand_beach": dict(base="beach", grass="#7fdc54", foliage="#5ccc48", water="#2fe3d4", wfog="#21b8bf",
                             sky="#6db7ff", fog="#d2ecff", particle=None, music="minecraft:music.overworld.cherry_grove",
                             veg=None, hw={9: ["trees_beach"]}),
    "black_sand_beach": dict(base="stony_shore", grass="#6fb44a", foliage="#4f9e3c", water="#22b4c8", wfog="#167d8f",
                             sky="#7fb0f0", fog="#c4d6e8", particle=("minecraft:white_ash", 0.002),
                             music="minecraft:music.overworld.sparse_jungle", veg=None, hw={9: ["trees_beach"]}),
    "motu_islets": dict(base="beach", grass="#7fdc54", foliage="#5ccc48", water="#2fe3d4", wfog="#21b8bf",
                        sky="#6db7ff", fog="#d2ecff", particle=None, music="minecraft:music.overworld.cherry_grove",
                        veg=None, hw={9: ["trees_motu", "flowers_light"]}),
    "coral_lagoon": dict(base="warm_ocean", grass="#5fd13e", foliage="#3fb43a", water="#2fe3d4", wfog="#21b8bf",
                         sky="#6db7ff", fog="#c7e4ff", particle=None, music="minecraft:music.overworld.cherry_grove",
                         veg=None, hw={}),
    "deep_reef_ocean": dict(base="deep_lukewarm_ocean", grass="#5fd13e", foliage="#3fb43a", water="#1fa4e0",
                            wfog="#0e5f9e", sky="#6db7ff", fog="#c7e4ff", particle=None,
                            music="minecraft:music.overworld.jungle", veg=None, hw={}, extra_veg=["warm_ocean_vegetation"]),
    "jungle_river": dict(base="river", grass="#47c936", foliage="#36b034", water="#42d9ee", wfog="#2ab0c4",
                         sky="#79b4ff", fog="#c7e6f0", particle=None, music="minecraft:music.overworld.jungle",
                         veg=None, extra_veg=["patch_sugar_cane", "patch_waterlily"], hw={9: ["trees_river", "ferns_light"]}),
    "lush_grotto": dict(base="lush_caves", grass="#5fd13e", foliage="#3fb43a", water="#3fd1e8", wfog="#2a9fb5",
                        sky="#79b4ff", fog="#c4e2ee", particle=("minecraft:spore_blossom_air", 0.008),
                        music="minecraft:music.overworld.lush_caves", veg=None, hw={}, keep_monsters=True),
}

# vanilla biomen die in de normale wereld tropisch worden (alleen nieuwe chunks)
OVERRIDES = {"jungle": "tropical_rainforest", "bamboo_jungle": "bamboo_valley", "sparse_jungle": "tiki_grove",
             "warm_ocean": "coral_lagoon"}

# vanilla biome -> paradise biome (voor de dimensie, zelfde klimaatkaart als vanilla)
BIOME_MAP = {
    "mushroom_fields": "motu_islets",
    "deep_frozen_ocean": "deep_reef_ocean", "deep_cold_ocean": "deep_reef_ocean", "deep_ocean": "deep_reef_ocean",
    "deep_lukewarm_ocean": "deep_reef_ocean",
    "frozen_ocean": "coral_lagoon", "cold_ocean": "coral_lagoon", "ocean": "coral_lagoon", "lukewarm_ocean": "coral_lagoon",
    "warm_ocean": "coral_lagoon",
    "beach": "white_sand_beach", "snowy_beach": "white_sand_beach", "stony_shore": "black_sand_beach",
    "river": "jungle_river", "frozen_river": "jungle_river",
    "swamp": "mangrove_coast", "mangrove_swamp": "mangrove_coast",
    "jungle": "tropical_rainforest", "sparse_jungle": "tiki_grove", "bamboo_jungle": "bamboo_valley",
    "dark_forest": "lost_jungle", "forest": "tropical_rainforest", "birch_forest": "tropical_rainforest",
    "old_growth_birch_forest": "lost_jungle",
    "flower_forest": "plumeria_valley", "cherry_grove": "plumeria_valley", "meadow": "plumeria_valley",
    "plains": "guarma_fields", "sunflower_plains": "guarma_fields", "savanna": "guarma_fields",
    "savanna_plateau": "guarma_highlands", "windswept_savanna": "guarma_highlands",
    "desert": "red_canyon", "badlands": "red_canyon", "eroded_badlands": "red_canyon", "wooded_badlands": "red_canyon",
    "taiga": "cloud_forest", "snowy_taiga": "cloud_forest", "old_growth_pine_taiga": "cloud_forest",
    "old_growth_spruce_taiga": "cloud_forest", "snowy_plains": "tiki_grove", "ice_spikes": "tiki_grove", "grove": "cloud_forest",
    "windswept_hills": "moorea_peaks", "windswept_gravelly_hills": "moorea_peaks", "windswept_forest": "cloud_forest",
    "snowy_slopes": "moorea_peaks", "jagged_peaks": "moorea_peaks", "frozen_peaks": "moorea_peaks", "stony_peaks": "moorea_peaks",
    "lush_caves": "lush_grotto", "dripstone_caves": "lush_grotto", "deep_dark": "lush_grotto",
}

# welke vanilla oppervlakte-regels een paradise-biome erft
SURF_MAP = {
    "beach": ["white_sand_beach", "motu_islets"],
    "badlands": ["red_canyon"], "eroded_badlands": ["red_canyon"], "wooded_badlands": ["red_canyon"],
    "warm_ocean": ["coral_lagoon"], "lukewarm_ocean": ["coral_lagoon"], "deep_lukewarm_ocean": ["deep_reef_ocean"],
    "mangrove_swamp": ["mangrove_coast"],
    "old_growth_pine_taiga": ["tropical_rainforest", "lost_jungle", "cloud_forest"],
    "old_growth_spruce_taiga": ["tropical_rainforest", "lost_jungle", "cloud_forest"],
    "windswept_savanna": ["guarma_highlands"],
}

CREATURES = {
    "tropical_rainforest": [("parrot", 40, 1, 2), ("ocelot", 3, 1, 1), ("chicken", 10, 2, 4), ("panda", 1, 1, 2), ("pig", 6, 2, 3)],
    "lost_jungle": [("parrot", 40, 1, 3), ("ocelot", 4, 1, 2)],
    "bamboo_valley": [("panda", 40, 1, 2), ("parrot", 20, 1, 2), ("chicken", 8, 2, 4)],
    "tiki_grove": [("parrot", 20, 1, 2), ("chicken", 12, 2, 4), ("pig", 6, 2, 3)],
    "plumeria_valley": [("rabbit", 8, 2, 3), ("bee", 10, 2, 3), ("parrot", 10, 1, 2)],
    "guarma_fields": [("horse", 6, 2, 5), ("cow", 8, 2, 4), ("chicken", 10, 2, 4), ("donkey", 2, 1, 3)],
    "guarma_highlands": [("horse", 4, 2, 4), ("goat", 6, 1, 3), ("llama", 3, 2, 4)],
    "moorea_peaks": [("goat", 12, 1, 3), ("parrot", 8, 1, 2)],
    "cloud_forest": [("parrot", 15, 1, 2), ("rabbit", 6, 1, 2)],
    "red_canyon": [("rabbit", 6, 1, 2), ("armadillo", 8, 1, 2)],
    "mangrove_coast": [("frog", 12, 2, 5), ("parrot", 10, 1, 2)],
    "white_sand_beach": [("turtle", 8, 2, 5)],
    "black_sand_beach": [("turtle", 15, 2, 5)],
    "motu_islets": [("turtle", 10, 2, 4), ("parrot", 5, 1, 2)],
    "jungle_river": [("frog", 10, 2, 4)],
}
WATER_CREATURE = {"coral_lagoon": [("dolphin", 2, 1, 2), ("squid", 2, 1, 2)], "deep_reef_ocean": [("dolphin", 3, 1, 3), ("squid", 4, 1, 4)]}
WATER_AMBIENT = {"coral_lagoon": [("tropical_fish", 25, 8, 8), ("pufferfish", 15, 1, 3)],
                 "deep_reef_ocean": [("tropical_fish", 25, 8, 8), ("pufferfish", 15, 1, 3)],
                 "jungle_river": [("tropical_fish", 10, 4, 6)], "mangrove_coast": [("tropical_fish", 25, 8, 8)]}


def spawns(table, name):
    return [{"type": f"minecraft:{t}", "maxCount": b, "minCount": a, "weight": w} for t, w, a, b in table.get(name, [])]


# ===================================================================== feature-volgorde
def master_order():
    """Topologische volgorde van alle vanilla features per stap (consistent met alle vanilla biomen)."""
    orders = {}
    for step in range(11):
        edges, nodes = {}, []
        for b in sorted(VBIOMES):
            lst = VBIOMES[b]["features"][step] if step < len(VBIOMES[b]["features"]) else []
            for f in lst:
                if f not in nodes:
                    nodes.append(f)
            for a, bb in zip(lst, lst[1:]):
                edges.setdefault(a, set()).add(bb)
        indeg = {n: 0 for n in nodes}
        for a in edges:
            for bb in edges[a]:
                indeg[bb] += 1
        out = []
        ready = [n for n in nodes if indeg[n] == 0]
        while ready:
            n = ready.pop(0)
            out.append(n)
            for bb in sorted(edges.get(n, ()), key=nodes.index):
                indeg[bb] -= 1
                if indeg[bb] == 0:
                    ready.append(bb)
        assert len(out) == len(nodes), "vanilla volgorde heeft een cyclus?"
        orders[step] = out
    return orders


ORDER = master_order()


def feature_lists(spec, name):
    base = VBIOMES[spec["base"]]["features"]
    lists = []
    for step in range(11):
        v = list(base[step]) if step < len(base) else []
        if step == 1:
            v = [f for f in v if f != "minecraft:lake_lava_surface"]
        if step == 9 and spec.get("veg") is not None:
            v = ["minecraft:" + f for f in spec["veg"]]
        if step == 9:
            v += ["minecraft:" + f for f in spec.get("extra_veg", [])]
        v = sorted(set(v), key=lambda f: ORDER[step].index(f))
        own = [H + f for f in HAWAII_ORDER.get(step, []) if f in spec["hw"].get(step, [])]
        lists.append(v + own)
    return lists


def biome_json(name, spec, vanilla_spawns=None):
    base = VBIOMES[spec["base"]]
    effects = {
        "fog_color": c(spec["fog"]), "foliage_color": c(spec["foliage"]), "grass_color": c(spec["grass"]),
        "mood_sound": {"block_search_extent": 8, "offset": 2.0, "sound": "minecraft:ambient.cave", "tick_delay": 6000},
        "music": {"max_delay": 24000, "min_delay": 12000, "replace_current_music": False, "sound": spec["music"]},
        "sky_color": c(spec["sky"]), "water_color": c(spec["water"]), "water_fog_color": c(spec["wfog"]),
    }
    if spec.get("particle"):
        effects["particle"] = {"options": {"type": spec["particle"][0]}, "probability": spec["particle"][1]}
    if vanilla_spawns is not None:
        spawners = copy.deepcopy(vanilla_spawns)
        extra = {"creature": spawns(CREATURES, name), "water_ambient": spawns(WATER_AMBIENT, name)}
        for k, v in extra.items():
            have = {e["type"] for e in spawners.get(k, [])}
            spawners.setdefault(k, []).extend(e for e in v if e["type"] not in have)
    elif spec.get("keep_monsters"):
        spawners = copy.deepcopy(base["spawners"])
    else:
        spawners = {"ambient": [], "axolotls": copy.deepcopy(base["spawners"].get("axolotls", [])), "creature": spawns(CREATURES, name),
                    "misc": [], "monster": [], "underground_water_creature": copy.deepcopy(base["spawners"].get("underground_water_creature", [])),
                    "water_ambient": spawns(WATER_AMBIENT, name), "water_creature": spawns(WATER_CREATURE, name)}
    return {
        "carvers": copy.deepcopy(base["carvers"]),
        "downfall": 0.9,
        "effects": effects,
        "features": feature_lists(spec, name),
        "has_precipitation": True,
        "spawn_costs": {},
        "spawners": spawners,
        "temperature": 0.95,
    }


# ===================================================================== oppervlak + dimensie
def rule_block(state):
    return {"type": "minecraft:block", "result_state": bs(state)}


def cond(test, then):
    return {"type": "minecraft:condition", "if_true": test, "then_run": then}


def floor(add=False, secondary=0):
    return {"type": "minecraft:stone_depth", "add_surface_depth": add, "offset": 0, "secondary_depth_range": secondary,
            "surface_type": "floor"}


def biome_is(*names):
    return {"type": "minecraft:biome", "biome_is": [H + n for n in names]}


def noise_band(lo, hi):
    return {"type": "minecraft:noise_threshold", "max_threshold": hi, "min_threshold": lo, "noise": "minecraft:surface"}


ABOVE_WATER = {"type": "minecraft:water", "add_stone_depth": False, "offset": -1, "surface_depth_multiplier": 0}


def surface_rules():
    vanilla = copy.deepcopy(VNOISE["surface_rule"])

    def walk(o):
        if isinstance(o, dict):
            if o.get("type") == "minecraft:biome":
                new = []
                for b in o["biome_is"]:
                    for m in SURF_MAP.get(b.split(":")[1], []):
                        if H + m not in new:
                            new.append(H + m)
                o["biome_is"] = new
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(vanilla)
    seq = vanilla["sequence"]
    peaks = cond(biome_is("moorea_peaks"), cond({"type": "minecraft:y_above", "add_stone_depth": False,
                                                  "anchor": {"absolute": 63}, "surface_depth_multiplier": 0},
                                                 {"type": "minecraft:sequence", "sequence": [
                                                     cond(floor(), {"type": "minecraft:sequence", "sequence": [
                                                         cond({"type": "minecraft:steep"}, rule_block("moss_block")),
                                                         cond(ABOVE_WATER, rule_block("grass_block[snowy=false]")),
                                                         rule_block("moss_block")]}),
                                                     cond(floor(True), rule_block("dirt")),
                                                     cond(noise_band(0.25, 10.0), rule_block("mossy_cobblestone")),
                                                     cond(noise_band(-0.15, 0.25), rule_block("moss_block")),
                                                     cond(noise_band(-0.4, -0.15), rule_block("andesite")),
                                                 ]}))
    shore = cond({"type": "minecraft:above_preliminary_surface"}, {"type": "minecraft:sequence", "sequence": [
        cond(biome_is("black_sand_beach"), {"type": "minecraft:sequence", "sequence": [
            cond(floor(), rule_block("black_concrete_powder")),
            cond(floor(True, 3), rule_block("basalt[axis=y]"))]}),
        cond(biome_is("motu_islets"), {"type": "minecraft:sequence", "sequence": [
            cond(floor(), rule_block("sand")),
            cond(floor(True, 4), rule_block("sandstone"))]}),
        cond(biome_is("jungle_river"), cond({"type": "minecraft:not", "invert": ABOVE_WATER}, {"type": "minecraft:sequence", "sequence": [
            cond(floor(), rule_block("sand")),
            cond(floor(True), rule_block("sand"))]})),
    ]})
    return {"type": "minecraft:sequence", "sequence": [seq[0], peaks, shore] + seq[1:]}


def noise_settings():
    ns = copy.deepcopy(VNOISE)
    ns["surface_rule"] = surface_rules()
    return ns


def dimension():
    d = copy.deepcopy(VDIM)
    for e in d["generator"]["biome_source"]["biomes"]:
        e["biome"] = H + BIOME_MAP[e["biome"].split(":")[1]]
    d["generator"]["settings"] = H + "paradise"
    d["type"] = "minecraft:overworld"
    return d


# ===================================================================== structuren
STRUCTS = {
    # naam: (biomen, spacing, separation, salt, aanpassing, hoogte-offset, heightmap)
    "lost_temple": (["tropical_rainforest", "lost_jungle", "bamboo_valley"], 34, 12, 81273641, "beard_box", -1, "WORLD_SURFACE_WG"),
    "plaza": (["tropical_rainforest", "lost_jungle", "tiki_grove", "plumeria_valley", "guarma_fields", "cloud_forest"], 22, 8, 81273642, "beard_thin", -1, "WORLD_SURFACE_WG"),
    "idol_head": (["tropical_rainforest", "lost_jungle", "cloud_forest", "guarma_highlands", "red_canyon", "moorea_peaks", "tiki_grove"], 24, 9, 81273643, "beard_thin", -4, "WORLD_SURFACE_WG"),
    "shrine": (["tropical_rainforest", "lost_jungle", "bamboo_valley", "tiki_grove", "plumeria_valley", "guarma_fields", "guarma_highlands", "cloud_forest", "moorea_peaks"], 13, 5, 81273644, "beard_thin", -1, "WORLD_SURFACE_WG"),
    "abandoned_tiki_bar": (["white_sand_beach", "motu_islets"], 16, 6, 81273645, "beard_thin", 0, "WORLD_SURFACE_WG"),
    "collapsed_fales": (["tiki_grove", "guarma_fields", "plumeria_valley", "mangrove_coast"], 20, 7, 81273646, "beard_thin", -1, "WORLD_SURFACE_WG"),
    "aqueduct": (["tropical_rainforest", "lost_jungle", "cloud_forest", "red_canyon", "guarma_highlands"], 26, 9, 81273647, "beard_thin", -1, "WORLD_SURFACE_WG"),
    "sunken_ruins": (["coral_lagoon", "deep_reef_ocean"], 16, 6, 81273648, "none", 0, "OCEAN_FLOOR_WG"),
}
# overworld-biomen die ook ruines krijgen
STRUCT_OVERWORLD = {"lost_temple": ["jungle", "bamboo_jungle"], "plaza": ["jungle", "sparse_jungle"],
                    "idol_head": ["jungle", "sparse_jungle"], "shrine": ["jungle", "bamboo_jungle", "sparse_jungle"],
                    "aqueduct": ["jungle"], "sunken_ruins": ["warm_ocean"], "collapsed_fales": ["sparse_jungle"]}
VANILLA_TAGS = {
    "has_structure/shipwreck": ["coral_lagoon", "deep_reef_ocean"],
    "has_structure/shipwreck_beached": ["white_sand_beach", "black_sand_beach", "motu_islets"],
    "has_structure/buried_treasure": ["white_sand_beach", "black_sand_beach", "motu_islets"],
    "has_structure/ocean_ruin_warm": ["coral_lagoon", "deep_reef_ocean"],
    "has_structure/jungle_temple": ["tropical_rainforest", "lost_jungle", "bamboo_valley"],
    "has_structure/mineshaft": [b for b in BIOMES if b not in ("coral_lagoon", "deep_reef_ocean", "lush_grotto")],
    "has_structure/ruined_portal_jungle": ["tropical_rainforest", "lost_jungle", "bamboo_valley", "tiki_grove"],
    "has_structure/ruined_portal_ocean": ["coral_lagoon", "deep_reef_ocean"],
    "has_structure/trail_ruins": ["tropical_rainforest", "lost_jungle", "cloud_forest"],
    "is_jungle": ["tropical_rainforest", "lost_jungle", "bamboo_valley", "tiki_grove"],
    "is_ocean": ["coral_lagoon", "deep_reef_ocean"],
    "is_deep_ocean": ["deep_reef_ocean"],
    "is_beach": ["white_sand_beach", "black_sand_beach", "motu_islets"],
    "is_river": ["jungle_river"],
    "is_mountain": ["moorea_peaks"],
    "is_overworld": list(BIOMES),
    "allows_tropical_fish_spawns_at_any_height": ["coral_lagoon", "deep_reef_ocean"],
    "spawns_warm_variant_frogs": [b for b in BIOMES],
    "stronghold_biased_to": [b for b in BIOMES if b not in ("coral_lagoon", "deep_reef_ocean", "jungle_river", "lush_grotto")],
}


# ===================================================================== schrijven
def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n")


def run(root):
    data = root / "hawaii_beach" / "data"
    hw = data / "hawaii"
    mc = data / "minecraft"
    import shutil
    for d in (hw / "worldgen" / "configured_feature", hw / "worldgen" / "placed_feature", hw / "worldgen" / "structure",
              hw / "worldgen" / "structure_set", hw / "worldgen" / "template_pool", hw / "worldgen" / "processor_list",
              hw / "worldgen" / "noise_settings", hw / "worldgen" / "world_preset", hw / "dimension", hw / "structure" / "ruins", mc / "worldgen",
              mc / "tags" / "worldgen", hw / "tags" / "worldgen"):
        if d.exists():
            shutil.rmtree(d)
    files = {}

    def out(rel, obj):
        files[rel] = obj
        write_json(data / rel, obj)

    for n, o in CONFIGURED.items():
        out(f"hawaii/worldgen/configured_feature/{n}.json", o)
    for n, o in SELECTORS.items():
        out(f"hawaii/worldgen/configured_feature/{n}.json", o)
    for n, o in PLACED.items():
        out(f"hawaii/worldgen/placed_feature/{n}.json", o)
    for n, spec in BIOMES.items():
        out(f"hawaii/worldgen/biome/{n}.json", biome_json(n, spec))
    for van, mine in OVERRIDES.items():
        out(f"minecraft/worldgen/biome/{van}.json", biome_json(mine, dict(BIOMES[mine], base=van),
                                                              vanilla_spawns=VBIOMES[van]["spawners"]))
    out("hawaii/worldgen/noise_settings/paradise.json", noise_settings())
    out("hawaii/dimension/paradise.json", dimension())
    # wereldtype "Tropical Paradise" bij het maken van een nieuwe wereld (hele overworld = paradise)
    preset = copy.deepcopy(VPRESET)
    preset["dimensions"]["minecraft:overworld"] = dimension()
    out("hawaii/worldgen/world_preset/tropical_paradise.json", preset)
    out("minecraft/tags/worldgen/world_preset/normal.json", {"replace": False, "values": [H + "tropical_paradise"]})
    # ruines
    rot = {"values": ["minecraft:stone_bricks", "minecraft:mossy_stone_bricks", "minecraft:cracked_stone_bricks",
                      "minecraft:cobblestone", "minecraft:mossy_cobblestone", "minecraft:tuff_bricks", "minecraft:hay_block",
                      "minecraft:bamboo_planks", "minecraft:stone", "minecraft:polished_tuff", "minecraft:tuff",
                      "minecraft:stone_brick_stairs", "minecraft:mossy_stone_brick_wall", "minecraft:andesite"]}
    out("hawaii/tags/block/ruin_rottable.json", rot)
    out("hawaii/worldgen/processor_list/overgrown_ruin.json", {"processors": [
        {"processor_type": "minecraft:rule", "rules": [
            {"input_predicate": {"block": "minecraft:stone_bricks", "predicate_type": "minecraft:random_block_match", "probability": 0.3},
             "location_predicate": {"predicate_type": "minecraft:always_true"}, "output_state": {"Name": "minecraft:mossy_stone_bricks"}},
            {"input_predicate": {"block": "minecraft:stone_bricks", "predicate_type": "minecraft:random_block_match", "probability": 0.15},
             "location_predicate": {"predicate_type": "minecraft:always_true"}, "output_state": {"Name": "minecraft:cracked_stone_bricks"}},
            {"input_predicate": {"block": "minecraft:cobblestone", "predicate_type": "minecraft:random_block_match", "probability": 0.4},
             "location_predicate": {"predicate_type": "minecraft:always_true"}, "output_state": {"Name": "minecraft:mossy_cobblestone"}},
            {"input_predicate": {"block": "minecraft:tuff_bricks", "predicate_type": "minecraft:random_block_match", "probability": 0.1},
             "location_predicate": {"predicate_type": "minecraft:always_true"}, "output_state": {"Name": "minecraft:moss_block"}},
        ]},
        {"integrity": 0.9, "processor_type": "minecraft:block_rot", "rottable_blocks": "#hawaii:ruin_rottable"},
        {"processor_type": "minecraft:protected_blocks", "value": "#minecraft:features_cannot_replace"},
    ]})
    tpl_states = set()
    for name, (fn, variants) in RUINS.items():
        elements = []
        for v in range(variants):
            t = fn(sum(map(ord, name)) * 31 + v)
            size, pal = t.write(_mkpath(hw / "structure" / "ruins" / f"{name}_{v}.nbt"))
            tpl_states |= pal
            elements.append({"element": {"element_type": "minecraft:single_pool_element",
                                         "location": f"{H}ruins/{name}_{v}", "processors": H + "overgrown_ruin",
                                         "projection": "rigid"}, "weight": 1})
        out(f"hawaii/worldgen/template_pool/ruins/{name}.json", {"elements": elements, "fallback": "minecraft:empty"})
        biomes, spacing, sep, salt, adapt, dy, hm = STRUCTS[name]
        tag_values = [H + b for b in biomes] + ["minecraft:" + b for b in STRUCT_OVERWORLD.get(name, [])]
        out(f"hawaii/tags/worldgen/biome/has_structure/{name}.json", {"values": tag_values})
        out(f"hawaii/worldgen/structure/{name}.json", {
            "type": "minecraft:jigsaw", "biomes": f"#{H}has_structure/{name}", "max_distance_from_center": 80,
            "project_start_to_heightmap": hm, "size": 1, "spawn_overrides": {}, "start_height": {"absolute": dy},
            "start_pool": f"{H}ruins/{name}", "step": "surface_structures", "terrain_adaptation": adapt,
            "use_expansion_hack": False})
        out(f"hawaii/worldgen/structure_set/{name}.json", {
            "placement": {"type": "minecraft:random_spread", "salt": salt, "separation": sep, "spacing": spacing},
            "structures": [{"structure": f"{H}{name}", "weight": 1}]})
    for tag, vals in VANILLA_TAGS.items():
        out(f"minecraft/tags/worldgen/biome/{tag}.json", {"replace": False, "values": [H + v for v in vals]})
    errors = validate(files, tpl_states)
    return files, errors


def _mkpath(p):
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


# ===================================================================== controle
def validate(files, tpl_states):
    errors = []
    own = {}
    for rel in files:
        parts = rel[:-5].split("/")
        ns_ = parts[0]
        if parts[1] == "worldgen":
            reg, name = "worldgen/" + parts[2], "/".join(parts[3:])
        elif parts[1] == "tags":
            reg, name = "tag/" + "/".join(parts[2:4] if parts[2] == "worldgen" else parts[2:3]), \
                "/".join(parts[4:] if parts[2] == "worldgen" else parts[3:])
        else:
            reg, name = parts[1], "/".join(parts[2:])
        own.setdefault(reg, set()).add(f"{ns_}:{name}")
    own.setdefault("structure", set()).update(f"{H}ruins/{n}_{v}" for n, (fn, k) in RUINS.items() for v in range(k))
    for t in VANILLA_TAGS:
        if t not in REG["tag/worldgen/biome"]:
            errors.append(f"vanilla biome-tag bestaat niet: {t}")

    def exists(registry, ident):
        ns_, name = ident.split(":", 1)
        if ns_ == "minecraft" and name in REG.get(registry, []):
            return True
        return ident in own.get(registry, set())

    def check_ref(key, val, ctx):
        if key in ("feature", "default") and isinstance(val, str):
            if not (exists("worldgen/placed_feature", val) or exists("worldgen/configured_feature", val)):
                errors.append(f"{ctx}: onbekende feature {val}")
        if key == "sound" and isinstance(val, str) and not exists("sound_event", val):
            errors.append(f"{ctx}: onbekend geluid {val}")
        if key == "type" and isinstance(val, str) and val.startswith("minecraft:") and ctx.endswith("particle"):
            pass

    def walk(o, ctx, parent_key=""):
        if isinstance(o, dict):
            if "Name" in o and isinstance(o["Name"], str):
                s = o["Name"] + ("[" + ",".join(f"{k}={v}" for k, v in o.get("Properties", {}).items()) + "]" if o.get("Properties") else "")
                check_state(s, ctx)
            for k, v in o.items():
                check_ref(k, v, ctx)
                walk(v, ctx, k)
        elif isinstance(o, list):
            for v in o:
                walk(v, ctx, parent_key)

    def check_state(s, ctx):
        name, props = parse_state(s)
        if name in ("minecraft:water", "minecraft:lava") and set(props) <= {"falling", "level"}:
            return  # vloeistof-state (bv. in een spring_feature)
        base = name.split(":")[1]
        blocks = MCDATA["blocks"]
        if base not in blocks:
            errors.append(f"{ctx}: onbekend blok {s}")
            return
        for k, v in props.items():
            if k not in blocks[base] or v not in blocks[base][k]:
                errors.append(f"{ctx}: ongeldige eigenschap {k}={v} in {s}")

    for rel, obj in files.items():
        walk(obj, rel)
        if "/worldgen/biome/" in rel and "/tags/" not in rel:
            for step in obj["features"]:
                for f in step:
                    if not exists("worldgen/placed_feature", f):
                        errors.append(f"{rel}: onbekende placed feature {f}")
            for lst in obj["carvers"].values():
                for f in lst:
                    if f.split(":")[1] not in REG.get("worldgen/configured_carver", [f.split(":")[1]]):
                        errors.append(f"{rel}: onbekende carver {f}")
            for cat in obj["spawners"].values():
                for e in cat:
                    if e["type"].split(":")[1] not in MCDATA["entities"] and e["type"].split(":")[1] not in REG["entity_type"]:
                        errors.append(f"{rel}: onbekende mob {e['type']}")
            p = obj["effects"].get("particle")
            if p and p["options"]["type"].split(":")[1] not in REG["particle_type"]:
                errors.append(f"{rel}: onbekend deeltje {p['options']['type']}")
            if obj["effects"]["music"]["sound"].split(":")[1] not in REG["sound_event"]:
                errors.append(f"{rel}: onbekende muziek {obj['effects']['music']['sound']}")
        if "/structure/" in rel and "template_pool" not in rel and "structure_set" not in rel:
            pass
    for s in tpl_states:
        check_state(s, "template")
    # loot tables in templates
    for name in ("jungle_temple", "buried_treasure", "shipwreck_supply", "underwater_ruin_big", "village/village_fisher"):
        if f"chests/{name}" not in REG["loot_table"]:
            errors.append(f"onbekende loot table chests/{name}")
    # dimensie: elke biome moet bestaan
    dim = files["hawaii/dimension/paradise.json"]
    for e in dim["generator"]["biome_source"]["biomes"]:
        if not exists("worldgen/biome", e["biome"]):
            errors.append(f"dimensie: onbekende biome {e['biome']}")
            break
    for d in ("minecraft:overworld",):
        if d.split(":")[1] not in REG["dimension_type"]:
            errors.append("onbekend dimension type")
    # alle gebruikte types moeten bestaan in 1.21.1
    type_regs = [k for k in REG if k.endswith("_type") or k in (
        "worldgen/feature", "worldgen/structure_processor", "worldgen/structure_pool_element", "rule_test",
        "pos_rule_test", "worldgen/material_condition", "worldgen/material_rule", "worldgen/structure_placement")]
    known = set().union(*(set(REG[k]) for k in type_regs))
    for rel, obj in files.items():
        if "/dimension/" in rel or "noise_settings" in rel or "world_preset" in rel:
            continue
        for t in re.findall(r'"(?:type|processor_type|predicate_type|element_type)": "minecraft:([a-z_]+)"', json.dumps(obj)):
            if t not in known:
                errors.append(f"{rel}: onbekend type minecraft:{t}")
    surf = json.dumps(files["hawaii/worldgen/noise_settings/paradise.json"]["surface_rule"])
    for t in set(re.findall(r'"type": "minecraft:([a-z_]+)"', surf)):
        if t not in set(REG.get("worldgen/material_condition", [])) | set(REG.get("worldgen/material_rule", [])):
            errors.append(f"surface rule: onbekend type minecraft:{t}")
    errors += feature_cycles(files)
    return errors


def feature_cycles(files):
    """Bootst de 'feature order cycle' controle van Minecraft na voor de overworld en de paradise-dimensie."""
    errs = []
    ours = {rel.split("/")[-1][:-5]: obj for rel, obj in files.items() if rel.startswith("hawaii/worldgen/biome/")}
    over = {rel.split("/")[-1][:-5]: obj for rel, obj in files.items() if rel.startswith("minecraft/worldgen/biome/")}
    overworld = {b: (over.get(b) or VBIOMES[b])["features"] for b in VBIOMES}
    paradise = {b: o["features"] for b, o in ours.items()}
    for dim_name, biomes in (("overworld", overworld), ("paradise", paradise)):
        for step in range(11):
            edges = {}
            for b, feats in biomes.items():
                lst = feats[step] if step < len(feats) else []
                for a, c2 in zip(lst, lst[1:]):
                    edges.setdefault(a, set()).add(c2)
            # cyclus-detectie
            state = {}

            def dfs(n):
                state[n] = 1
                for m in edges.get(n, ()):
                    if state.get(m) == 1:
                        return True
                    if state.get(m) is None and dfs(m):
                        return True
                state[n] = 2
                return False
            for n in list(edges):
                if state.get(n) is None and dfs(n):
                    errs.append(f"feature order cycle in {dim_name}, stap {step}")
                    break
    return errs
