#                image_path,                             name,         id,         type, state, breakable, drops
sky_id =        ("images/tiles/sky.png",                "sky",          0,      "block", 0,     0,          0)
invisible_id =  ("images/tiles/invisible.png",          "invisible",    1,      "block", 1,     0,          1)
bedrock_id =    ("images/tiles/bedrock.png",            "bedrock",      2,      "block", 1,     0,          2)
grass_id =      ("images/tiles/grass.png",              "grass",        3,      "block", 1,     1,          4)
dirt_id =       ("images/tiles/dirt.png",               "dirt",         4,      "block", 1,     1,          4)
stone_id =      ("images/tiles/stone.png",              "stone",        5,      "block", 1,     1,          5)
sand_id =       ("images/tiles/sand.png",               "sand",         6,      "block", 1,     1,          6)
wood_id =       ("images/tiles/wood.png",               "wood",         7,      "block", 0,     1,          7)
leaf_id =       ("images/tiles/leaf.png",               "leaf",         8,      "block", 0,     1,          8)
chest_id =      ("images/tiles/chest.png",              "chest",        9,      "block", 1,     1,          9)
diamond_id =    ("images/tiles/diamond ore.png",        "diamond ore",  10,     "block", 1,     1,          10)
torch_id =      ("images/tiles/torch.png",              "torch",        11,     "block", 0,     1,          11)

pistol_id =     ("images/items/pistol.png",             "pistol",       100,     "item")


all_ids =  [sky_id,
            invisible_id,
            bedrock_id,
            grass_id,
            dirt_id,
            stone_id,
            sand_id,
            wood_id,
            leaf_id,
            chest_id,
            diamond_id,
            torch_id,
            pistol_id]

empty_list = [None for i in range(256)]
for i in all_ids:
    empty_list[i[2]] = i
    
id_list = empty_list