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

import pygame, sys, random, math, ConfigParser, time, threading
import pygame._view
import cPickle as pickle
from pygame.locals import *
from PodSixNet.Connection import connection, ConnectionListener

#Networking class
class Client(ConnectionListener):
    def __init__(self, host, port):
        self.Connect((host, port))
        self.players = []
        self.world = None
        self.projectiles = []
        self.lights = [[0 for i in xrange(WORLD_WIDTH)] for j in xrange(WORLD_HEIGHT)]
    
    def Loop(self):
        self.Pump()
        connection.Pump()
    
    def lightThread(self):
        self.lights = calculateLight()
    
    def Network(self, data):
        #print 'network:', data
        pass
    
    def Network_world(self, data):
        self.world = pickle.loads(data["world"])

    def Network_blockChange(self, data):
        self.world[data["x"]][data["y"]] = Data(data["id"],metadata=data["metadata"])
        threading.Thread(target=self.lightThread).start()
    
    def Network_posChange(self, data):
        pass
    
    def Network_players(self, data):
        self.players = data["players"]
        
    def Network_projectiles(self, data):
        self.projectiles = data["projectiles"]

    def Network_addToInv(self, data):
        addToInv(data["id"], data["amount"])
    
    def Network_uuid(self, data):
        self.uuid = data["uuid"]
        
    def Network_error(self, data):
        print data
        import traceback
        traceback.print_exc()
        connection.Close()

#Id is a metaclass for tiles and will be a metaclass for items in the future (such as weapons or tools)
class Id:
    def __init__(self, image_path, name, id, type):
        self.image = pygame.image.load(image_path).convert()
        self.rect = self.image.get_rect()
        self.name = name
        self.type = type
        self.id = id
        ids[id] = self #adds itself to the list of ids

#A tile is an id that can be placed and broken
class Tile(Id):
    def __init__(self, image_path, name, id, type, state, breakable, drops):
        Id.__init__(self, image_path, name, id, type)
        self.state = state
        self.breakable = breakable
        self.drops = drops
        
# class Container:
#     def __init__(self):
#         self.inv = [None for i in range(9)]
#         
#     def getInvSlot(id):
#         indexer = dict((p['id'], i) for i, p in enumerate(self.inv) if self.inv[i] is not None)
#         return indexer.get(id)
#     
#     def getItemAmount(id):
#         index = getInvSlot(id)
#         if index is not None:
#             return self.inv[index]["quantity"]
#         else:
#             return None
#         
#     def getSlotAmount(slot):
#         if self.inv[slot] is not None:
#             return self.inv[slot]["quantity"]
#         else:
#             return 0
#         
#     def addToInv(id, amount):
#         indexer = dict((p['id'], i) for i, p in enumerate(self.inv) if self.inv[i] is not None)
#         if indexer.get(id) is not None:
#             if self.inv[indexer.get(id)]["quantity"] + amount <= 0:
#                 self.inv[indexer.get(id)] = None
#             else:
#                 self.inv[indexer.get(id)]["quantity"] += amount
#         else:
#             for i in range(len(self.inv)):
#                 if self.inv[i] is None:
#                     self.inv[i] = {"id": id, "quantity": amount}
#                     break


#Data is an id that has metadata (such as what items are in a chest)
class Data:
    def __init__(self, id, metadata=None):
        self.id = id
        self.metadata = metadata
        if self.id == 9 and self.metadata == None:
            self.metadata = [None for i in range(5)]
        
class Character:
    def __init__(self, image_path, name):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.name = name
        self.jumping = False
        self.yVel = 0
        self.progress = 0 #To be used when blocks take time to break

class Projectile:
    def __init__(self, width, height, pos, color):
        self.width = width
        self.height = height
        self.color = color
        self.pos = pos


def getId(id):
    return ids[id]

def getInvSlot(id, data=None):
    if data == None:
        indexer = dict((p['id'], i) for i, p in enumerate(inv) if inv[i] is not None)
        return indexer.get(id)
    else:
        indexer = dict((p['id'], i) for i, p in enumerate(data) if data[i] is not None)
        return indexer.get(id)

def getItemAmount(id, data=None):
    if data == None:
        index = getInvSlot(id)
        if index is not None:
            return inv[index]["quantity"]
        else:
            return None
    else:
        index = getInvSlot(id, data=data)
        if index is not None:
            return data[index]["quantity"]
        else:
            return None
def getSlotAmount(slot, data=None):
    if data == None:
        if inv[slot] is not None:
            return inv[slot]["quantity"]
        else:
            return 0
    else:
        if data[slot] is not None:
            return data[slot]["quantity"]
        else:
            return 0

def addToInv(id, amount, data=None):
    if data == None:
        indexer = dict((p['id'], i) for i, p in enumerate(inv) if inv[i] is not None)
        if indexer.get(id) is not None:
            if inv[indexer.get(id)]["quantity"] + amount <= 0:
                inv[indexer.get(id)] = None
            else:
                inv[indexer.get(id)]["quantity"] += amount
        else:
            for i in range(len(inv)):
                if inv[i] is None:
                    inv[i] = {"id": id, "quantity": amount}
                    break
    else:
        indexer = dict((p['id'], i) for i, p in enumerate(data) if data[i] is not None)
        if indexer.get(id) is not None:
            if data[indexer.get(id)]["quantity"] + amount <= 0:
                data[indexer.get(id)] = None
            else:
                data[indexer.get(id)]["quantity"] += amount
        else:
            for i in range(len(data)):
                if data[i] is None:
                    data[i] = {"id": id, "quantity": amount}
                    break


def calculateLight():
    ct = time.time()
    lights = [[0 for i in xrange(WORLD_WIDTH)] for j in xrange(WORLD_HEIGHT)]
    world = c.world
    for x in xrange(WORLD_WIDTH):
        current_light = 0
        for y in xrange(WORLD_HEIGHT):
            if world[x][y].id == 0:
                current_light = 255
                lights[x][y] = 255
            else:
                if lights[x][y] > current_light:
                    current_light = lights[x][y]
                elif current_light != 0:
                    lights[x][y] = current_light
                if lights[x][y] == current_light and ids[world[x][y].id].state == 1:
                    current_light -= 25
    for x in xrange(WORLD_WIDTH):
        current_light = 0
        for y in xrange(WORLD_HEIGHT):
            if world[x][WORLD_HEIGHT-y-1].id == 0:
                current_light = 255
                lights[x][WORLD_HEIGHT-y-1] = 255
            else:
                if lights[x][WORLD_HEIGHT-y-1] > current_light:
                    current_light = lights[x][WORLD_HEIGHT-y-1]
                elif current_light != 0:
                    lights[x][WORLD_HEIGHT-y-1] = current_light
                if lights[x][WORLD_HEIGHT-y-1] == current_light and ids[world[x][WORLD_HEIGHT-y-1].id].state == 1:
                    current_light -= 25
    for y in xrange(WORLD_HEIGHT):
        current_light = 0
        for x in xrange(WORLD_WIDTH):
            if world[x][y].id == 0:
                current_light = 255
                lights[x][y] = 255
            else:
                if lights[x][y] > current_light:
                    current_light = lights[x][y]
                elif current_light != 0:
                    lights[x][y] = current_light
                if lights[x][y] == current_light and ids[world[x][y].id].state == 1:
                    current_light -= 25
    for y in xrange(WORLD_HEIGHT):
        current_light = 0
        for x in xrange(WORLD_WIDTH):
            if world[WORLD_WIDTH-x-1][y].id == 0:
                current_light = 255
                lights[WORLD_WIDTH-x-1][y] = 255
            else:
                if lights[WORLD_WIDTH-x-1][y] > current_light:
                    current_light = lights[WORLD_WIDTH-x-1][y]
                elif current_light != 0:
                    lights[WORLD_WIDTH-x-1][y] = current_light
                if lights[WORLD_WIDTH-x-1][y] == current_light and ids[world[WORLD_WIDTH-x-1][y].id].state == 1:
                    current_light -= 25
    print "Lighting update took " + str(time.time() - ct) + " seconds"
    return lights
                
def drawBlocks(camera):
    x = -(camera.x % 16)
    for i in range(int(math.floor(camera.x/16.0)), int(math.ceil((camera.x + camera.width)/16.0))):
        y = -(camera.y % 16)
        for j in range(int(math.floor(camera.y/16.0)), int(math.ceil((camera.y + camera.height)/16.0))):
            try:
                screen.blit(getId(c.world[i][j].id).image,[x,y])
            except:
                screen.blit(getId(0).image,[x,y])
            lightBack.set_alpha(255 - c.lights[i][j])
            screen.blit(lightBack,[x,y])
            y += 16
        x += 16

 
def drawInventory():
    screen.blit(inventoryBar, ((WINDOW_WIDTH - 328) / 2, WINDOW_HEIGHT - 40))
    back = pygame.Surface((32,32)).convert()
    back.set_alpha(128)
    back.fill((128,128,128)) 
    for i in range(len(inv)):
        if inv[i] is not None:
            screen.blit(pygame.transform.scale2x(ids[inv[i]["id"]].image), (((WINDOW_WIDTH - 328) / 2) + 32*i + 4*(i+1), WINDOW_HEIGHT - 36))
            text = str(inv[i]["quantity"])
            text_surf = inv_font.render(text, 1, (0,0,0))
            screen.blit(text_surf, (((WINDOW_WIDTH - 328) / 2) + 32*i + 4*(i+1) + (32 - inv_font.size(text)[0]), WINDOW_HEIGHT - 36))
        else:
            screen.blit(back, (((WINDOW_WIDTH - 328) / 2) + 32*i + 4*(i+1), WINDOW_HEIGHT - 36))
    for i in range(4):
        pygame.draw.rect(screen, (128, 128, 128), (((WINDOW_WIDTH - 328) / 2) + 36 * selected + i, WINDOW_HEIGHT - 40 + i, 40 - 2*i, 40 - 2*i), 1)

def drawName(name,x,y):
    text_surf = inv_font.render(name, 1, (0,0,0))
    screen.blit(text_surf, (x+8-(text_surf.get_width()/2)-camera.x, y-10-camera.y))

def drawChest(metadata,x,y):
    screen.blit(chestBar, (x+8-(chestBar.get_width()/2)-camera.x, y-20-camera.y))
    back = pygame.Surface((16,16)).convert()
    back.set_alpha(128)
    back.fill((128,128,128))
    for i in range(len(metadata)):
        if metadata[i] is not None:
            screen.blit(ids[metadata[i]["id"]].image, (x+8-(chestBar.get_width()/2)-camera.x + 16*i + 2*(i+1), y-18-camera.y))
            text = str(metadata[i]["quantity"])
            text_surf = inv_font.render(text, 1, (0,0,0))
            screen.blit(text_surf, (x+8-(chestBar.get_width()/2)-camera.x + 16*i + 2*(i+1) + (16 - inv_font.size(text)[0]), y-18-camera.y))
        else:
            screen.blit(back, (x+8-(chestBar.get_width()/2)-camera.x + 16*i + 2*(i+1), y-18-camera.y))
            
def drawProjectiles(projectiles):
    for i in projectiles:
        pygame.draw.rect(screen, i[3], (i[0][0] - camera.x, i[0][1] - camera.y, i[1], i[2]))


def updateGrass(world, camera=None):
    if camera:
        x = -(camera.x % 16)
        for i in range(int(math.floor(camera.x/16.0)), int(math.ceil((camera.x + camera.width)/16.0))):
            y = -(camera.y % 16)
            for j in range(int(math.floor(camera.y/16.0)), int(math.ceil((camera.y + camera.height)/16.0))):
                try:
                    if world[i][j].id == 4 and world[i][j-1].id == 0:
                        world[i][j] = Data(3)
                    if world[i][j].id == 3 and world[i][j-1].id != 0:
                        world[i][j] = Data(4)
                except:
                    pass
                y += 16
            x += 16
    else:
        for x in range(WORLD_WIDTH):
            for y in range(WORLD_HEIGHT):
                if world[x][y].id == 4 and world[x][y-1].id == 0:
                    world[x][y] = Data(3)
                
def setCam(cam, char):
    cam.x = char.rect.x - WINDOW_WIDTH/2
    cam.y = char.rect.y - WINDOW_HEIGHT/2

    if cam.x < 0:
        cam.x = 0
    if cam.y < 0:
        cam.y = 0
    if cam.x > WORLD_WIDTH_PX - WINDOW_WIDTH:
        cam.x = WORLD_WIDTH_PX - WINDOW_WIDTH
    if cam.y > WORLD_HEIGHT_PX - WINDOW_HEIGHT:
        cam.y = WORLD_HEIGHT_PX - WINDOW_HEIGHT
        
def gravity(char):
    if char.yVel >= 0:
        if getId(c.world[(char.rect.left + 1) / 16][char.rect.bottom / 16].id).state == 1 or getId(c.world[(char.rect.right - 1) / 16][char.rect.bottom / 16].id).state == 1:
            char.jumping = False
            char.yVel = 0
            return
        else:
            char.jumping = True
            char.yVel += .5
            if getId(c.world[(char.rect.left + 1) / 16][int((char.rect.bottom + char.yVel) / 16)].id).state == 0 and getId(c.world[(char.rect.right - 1) / 16][int((char.rect.bottom + char.yVel) / 16)].id).state == 0:
                char.rect.y += char.yVel
            else:
                char.rect.y += 1
    else:
        if getId(c.world[(char.rect.left + 1) / 16][char.rect.y / 16 + 1].id).state == 1 or getId(c.world[(char.rect.right - 1) / 16][char.rect.y / 16 + 1].id).state == 1:
            char.jumping = False
            char.yVel = 0
            return
        else:
            char.jumping = True
            char.yVel += .5
            if getId(c.world[(char.rect.left + 1) / 16][int((char.rect.y + char.yVel) / 16)].id).state == 0 and getId(c.world[(char.rect.right - 1) / 16][int((char.rect.y + char.yVel) / 16)].id).state == 0:
                char.rect.y += char.yVel
            elif getId(c.world[(char.rect.left + 1) / 16][(char.rect.y - 1) / 16].id).state == 0 and getId(c.world[(char.rect.right - 1) / 16][(char.rect.y - 1) / 16].id).state == 0:
                char.rect.y -= 1


def resetPosition():
    character.rect.topleft = ((WORLD_WIDTH_PX-16)/2, 0) #initial position is in the sky in the middle of the map
    character.rect.x = character.rect.x/16*16
    while not (getId(c.world[(character.rect.left + 1) / 16][character.rect.bottom / 16].id).state == 1 or getId(c.world[(character.rect.right - 1) / 16][character.rect.bottom / 16].id).state == 1):
        character.rect.y += 1 #lower player until they hit ground

#constants
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
TILE_SIZE_X = 16
TILE_SIZE_Y = 16
WORLD_WIDTH_PX = 2048
WORLD_HEIGHT_PX = 2048
WORLD_WIDTH = WORLD_WIDTH_PX/TILE_SIZE_X
WORLD_HEIGHT = WORLD_HEIGHT_PX/TILE_SIZE_Y

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Block Fun")
    pygame.display.set_icon(pygame.image.load("images/tiles/grass.png"))
    screen = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
    
    inv_font =  pygame.font.Font(None, 14)
    
    camera = pygame.Rect(0,0,WINDOW_WIDTH,WINDOW_HEIGHT)
    
    ids = [None for i in range(256)]
    
    #                image_path,                             name,         id,         type, state, breakable, drops
    sky_tile = Tile("images/tiles/sky.png",                 "sky",          0,      "block", 0,     0,          0)
    invisible_tile = Tile("images/tiles/invisible.png",     "invisible",    1,      "block", 1,     0,          1)
    bedrock_tile = Tile("images/tiles/bedrock.png",         "bedrock",      2,      "block", 1,     0,          2)
    grass_tile = Tile("images/tiles/grass.png",             "grass",        3,      "block", 1,     1,          4)
    dirt_tile = Tile("images/tiles/dirt.png",               "dirt",         4,      "block", 1,     1,          4)
    stone_tile = Tile("images/tiles/stone.png",             "stone",        5,      "block", 1,     1,          5)
    sand_tile = Tile("images/tiles/sand.png",               "sand",         6,      "block", 1,     1,          6)
    wood_tile = Tile("images/tiles/wood.png",               "wood",         7,      "block", 0,     1,          7)
    leaf_tile = Tile("images/tiles/leaf.png",               "leaf",         8,      "block", 0,     1,          8)
    chest_tile = Tile("images/tiles/chest.png",             "chest",        9,      "block", 1,     1,          9)
    diamond_tile = Tile("images/tiles/diamond ore.png",     "diamond ore",  10,     "block", 1,     1,          10)
    torch_tile = Tile("images/tiles/torch.png",             "torch",        11,     "block", 0,     1,          11)
    
    pistol_item = Id("images/items/pistol.png",             "pistol",       100,     "item",)
    
    
    inventoryBar =  pygame.image.load("images/bar.png").convert_alpha()
    chestBar = pygame.image.load("images/bar_small.png").convert_alpha()
    
    clock = pygame.time.Clock()
    
    character = Character("images/character.png", "User")
    
    # real_tiles = [ids[i] for i in range(len(ids)) if ids[i] is not None]
    # breakables = [real_tiles[i] for i in range(len(real_tiles)) if real_tiles[i].breakable]
    # breakables.remove(3) #cant get grass because grass drops dirt
    
    inv = [None for i in range(9)]
    
    frame = 0
    
    selected = 0
    
    Config = ConfigParser.ConfigParser()
    Config.read("config.ini")
    ip = Config.get("connection", "ip")
    port = int(Config.get("connection", "port"))
    name = Config.get("connection", "name")
    
    if name == "":
    #     sys.exit()
        name = "User"
    
    c = Client(ip, port) #connect to server
    while c.world == None: #wait for world from server
        c.Loop()
        
    c.lights = calculateLight() #calculates initial lighting
    
    c.name = name
    c.Send({"action": "name", "name": c.name}) #sends username to server
    
    # print [[c.world[i][j].id for i in range(len(c.world))] for j in range(len(c.world[i]))]
    
    resetPosition() #start character in middle of map
    
    #Gives currently unobtainable items to player
    addToInv(9,5)
    addToInv(6,100)
    addToInv(2,100)
    addToInv(11,100)
    addToInv(100,1)
    
    #creates lighting tile
    lightBack = pygame.Surface((16,16)).convert()
    lightBack.fill((0,0,0))
    
    #main game loop
    while True:
        clock.tick(60)
        c.Loop()
        c.Send({"action": "posChange", "x": character.rect.x, "y": character.rect.y}) #sends character position to server
        
        #gets input
        key = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_press = pygame.mouse.get_pressed()
        hovered_data = c.world[(mouse_pos[0] + camera.x)/16][(mouse_pos[1]+ camera.y)/16]
        hovered = getId(hovered_data.id)
        
        if key[K_a]:    
            if getId(c.world[(character.rect.left - 1)/16][character.rect.top / 16].id).state == 0 and getId(c.world[(character.rect.left - 1) / 16][(character.rect.bottom - 1) / 16].id).state == 0:
                character.rect.x -= 1
        if key[K_d]:
            if getId(c.world[(character.rect.right + 1)/16][character.rect.top / 16].id).state == 0 and getId(c.world[(character.rect.right + 1) / 16][(character.rect.bottom - 1) / 16].id).state == 0:
                character.rect.x += 1
        if key[K_SPACE]:
            if not character.jumping and (getId(c.world[(character.rect.left + 1) / 16][character.rect.top / 16 - 1].id).state == 0 and getId(c.world[(character.rect.right - 1) / 16][character.rect.top / 16 - 1].id).state == 0):
                character.yVel = -8
                character.jumping = True
                character.rect.y -= 16
        #left click
        if mouse_press[0]:
            if inv[selected]["id"] == 100:
                #do gun stuff
                x_distance = mouse_pos[0] + camera.x - character.rect.x
                y_distance = mouse_pos[1] + camera.y - character.rect.y
                rotation_angle = math.atan2(y_distance, x_distance)
                c.Send({"action": "addProjectile", "width": 5, "height": 5, "startpos": character.rect.center, "speed": 10, "traveldistance": 400, "angle": rotation_angle, "color": (0,0,0)})
            elif hovered.breakable:
                #addToInv(hovered.drops, 1)
                c.Send({"action": "blockChange", "x": (mouse_pos[0] + camera.x)/16, "y": (mouse_pos[1]+ camera.y)/16, "id": 0, "metadata": None, "inv": hovered.drops, "amount": 1})
                #c.world[(mouse_pos[0] + camera.x)/16][(mouse_pos[1]+ camera.y)/16] = Data(0)
        #right click
        if mouse_press[2]:
            if hovered.id == 0:
                if getId(inv[selected]["id"]).type == "block":
                    if getSlotAmount(selected) != None:
                        if getSlotAmount(selected) > 0:
                            char_rect = pygame.Rect((character.rect.x - camera.x, character.rect.y - camera.y), (16, 32))
                            block_rect = pygame.Rect((mouse_pos[0] + camera.x ) / 16 * 16 - camera.x, (mouse_pos[1] + camera.y) / 16 * 16 - camera.y, 15, 15)
                            if not char_rect.colliderect(block_rect):
                                c.Send({"action": "blockChange", "x": (mouse_pos[0] + camera.x)/16, "y": (mouse_pos[1]+ camera.y)/16, "id": inv[selected]["id"], "metadata": None, "inv": inv[selected]["id"], "amount": -1})
                                #c.world[(mouse_pos[0] + camera.x)/16][(mouse_pos[1]+ camera.y)/16] = Data(inv[selected]["id"])
                                #addToInv(inv[selected]["id"], -1)
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                #scroll up
                if event.button == 4:
                    if selected == 0:
                        selected = 8
                    else:
                        selected -= 1
                #scroll down
                elif event.button == 5:
                    if selected == 8:
                        selected = 0
                    else:
                        selected += 1
            if event.type == KEYDOWN:
                #chest controls
                if event.key == K_1:
                    if getSlotAmount(0,data=hovered_data.metadata) > 0:
                        hover_id = hovered_data.metadata[0]["id"]
                        addToInv(hover_id,-1,data=hovered_data.metadata)
                        c.Send({"action": "blockChange", "x": (mouse_pos[0] + camera.x)/16, "y": (mouse_pos[1]+ camera.y)/16, "id": hovered_data.id, "metadata": hovered_data.metadata, "inv": hover_id, "amount": 1})
                if event.key == K_2:
                    if getSlotAmount(1,data=hovered_data.metadata) > 0:
                        hover_id = hovered_data.metadata[1]["id"]
                        addToInv(hover_id,-1,data=hovered_data.metadata)
                        c.Send({"action": "blockChange", "x": (mouse_pos[0] + camera.x)/16, "y": (mouse_pos[1]+ camera.y)/16, "id": hovered_data.id, "metadata": hovered_data.metadata, "inv": hover_id, "amount": 1})
                if event.key == K_3:
                    if getSlotAmount(2,data=hovered_data.metadata) > 0:
                        hover_id = hovered_data.metadata[2]["id"]
                        addToInv(hover_id,-1,data=hovered_data.metadata)
                        c.Send({"action": "blockChange", "x": (mouse_pos[0] + camera.x)/16, "y": (mouse_pos[1]+ camera.y)/16, "id": hovered_data.id, "metadata": hovered_data.metadata, "inv": hover_id, "amount": 1})
                if event.key == K_4:
                    if getSlotAmount(3,data=hovered_data.metadata) > 0:
                        hover_id = hovered_data.metadata[3]["id"]
                        addToInv(hover_id,-1,data=hovered_data.metadata)
                        c.Send({"action": "blockChange", "x": (mouse_pos[0] + camera.x)/16, "y": (mouse_pos[1]+ camera.y)/16, "id": hovered_data.id, "metadata": hovered_data.metadata, "inv": hover_id, "amount": 1})
                if event.key == K_5:
                    if getSlotAmount(4,data=hovered_data.metadata) > 0:
                        hover_id = hovered_data.metadata[4]["id"]
                        addToInv(hover_id,-1,data=hovered_data.metadata)
                        c.Send({"action": "blockChange", "x": (mouse_pos[0] + camera.x)/16, "y": (mouse_pos[1]+ camera.y)/16, "id": hovered_data.id, "metadata": hovered_data.metadata, "inv": hover_id, "amount": 1})
                if event.key == K_q:
                    if hovered_data.id == 9:
                        if getSlotAmount(selected) > 0:
                            addToInv(inv[selected]["id"],1,data=hovered_data.metadata)
                            c.Send({"action": "blockChange", "x": (mouse_pos[0] + camera.x)/16, "y": (mouse_pos[1]+ camera.y)/16, "id": hovered_data.id, "metadata": hovered_data.metadata, "inv": inv[selected]["id"], "amount": -1})
                        
        setCam(camera, character)
        gravity(character)
        updateGrass(c.world, camera)
        drawBlocks(camera)
        pygame.draw.rect(screen, (0,0,0), ((mouse_pos[0] + camera.x ) / 16 * 16 - camera.x, (mouse_pos[1] + camera.y) / 16 * 16 - camera.y, 16, 16), 1)
        for i in range(len(c.players)):
            if c.players[i][2] != c.uuid: #only use server data to draw other players; our player is drawn client side
                screen.blit(character.image, (c.players[i][0]-camera.x,c.players[i][1]-camera.y))
                drawName(c.players[i][3],c.players[i][0],c.players[i][1])
        screen.blit(character.image, (character.rect.x - camera.x, character.rect.y - camera.y))
        drawProjectiles(c.projectiles)
        drawName(c.name,character.rect.x,character.rect.y)
        if key[K_c]: #chests only show contents if c is held
            if hovered_data.metadata != None:
                drawChest(hovered_data.metadata,(mouse_pos[0] + camera.x)/16*16,(mouse_pos[1]+ camera.y)/16*16)
        drawInventory()
        pygame.display.update()
#         frame += 1
