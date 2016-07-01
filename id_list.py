# Copyright 2016 Evan Dunning
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#                image_path,                             name,         id,         type, state, breakable, drops, illuminant
sky_id =        ("images/tiles/sky.png",                "sky",          0,      "block", 0,     0,          0,      1)
invisible_id =  ("images/tiles/invisible.png",          "invisible",    1,      "block", 1,     0,          1,      0)
bedrock_id =    ("images/tiles/bedrock.png",            "bedrock",      2,      "block", 1,     0,          2,      0)
grass_id =      ("images/tiles/grass.png",              "grass",        3,      "block", 1,     1,          4,      0)
dirt_id =       ("images/tiles/dirt.png",               "dirt",         4,      "block", 1,     1,          4,      0)
stone_id =      ("images/tiles/stone.png",              "stone",        5,      "block", 1,     1,          5,      0)
sand_id =       ("images/tiles/sand.png",               "sand",         6,      "block", 1,     1,          6,      0)
wood_id =       ("images/tiles/wood.png",               "wood",         7,      "block", 0,     1,          7,      0)
leaf_id =       ("images/tiles/leaf.png",               "leaf",         8,      "block", 0,     1,          8,      0)
chest_id =      ("images/tiles/chest.png",              "chest",        9,      "block", 1,     1,          9,      0)
diamond_id =    ("images/tiles/diamond ore.png",        "diamond ore",  10,     "block", 1,     1,          10,     0)
torch_id =      ("images/tiles/torch.png",              "torch",        11,     "block", 0,     1,          11,     1)

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