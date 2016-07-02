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

import pygame, sys, math, ConfigParser, time
import pygame._view
import cPickle as pickle
from pygame.locals import *
from PodSixNet.Connection import connection, ConnectionListener
from data import Data

#Networking class
class Client(ConnectionListener):
    def __init__(self, host, port):
        self.Connect((host, port))
        self.health = 100
        self.players = []
        self.world = None
        self.projectiles = []
        self.lights = [[0 for i in xrange(WORLD_WIDTH)] for j in xrange(WORLD_HEIGHT)]
        self.time_shot = time.time()
    
    def Loop(self):
        self.Pump()
        connection.Pump()
    
    def Network(self, data):
        #print 'network:', data
        pass
    
    def Network_world(self, data):
        self.world = pickle.loads(data["world"])

    def Network_blockChange(self, data):
        self.world[data["x"]][data["y"]] = Data(data["id"],metadata=data["metadata"])
#         threading.Thread(target=self.lightThread).start()
        self.lights = calculateLight() #no longer need threads because of speed improvements
        updateGrass(self.world, camera)
    
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
        
    def Network_healthChange(self, data):
        self.health = data["health"]
        
    def Network_respawn(self, data):
        resetPosition()
        
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
    def __init__(self, image_path, name, id, type, state, breakable, drops, illuminant):
        Id.__init__(self, image_path, name, id, type)
        self.state = state
        self.breakable = breakable
        self.drops = drops
        self.illuminant = illuminant
        
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
    local_ids = ids
    lights = [[0 for i in xrange(WORLD_WIDTH)] for j in xrange(WORLD_HEIGHT)]
    world = c.world
    for x in xrange(WORLD_WIDTH):
        current_light = 0
        current_light2 = 0
        for y in xrange(WORLD_HEIGHT):
            if local_ids[world[x][y].id].illuminant == 1:
                current_light = 255
                lights[x][y] = 255
            else:
                if lights[x][y] > current_light:
                    current_light = lights[x][y]
                elif current_light != 0:
                    lights[x][y] = current_light
                if lights[x][y] == current_light and local_ids[world[x][y].id].state == 1:
                    current_light -= 25
            if local_ids[world[x][WORLD_HEIGHT-y-1].id].illuminant == 1:
                current_light2 = 255
                lights[x][WORLD_HEIGHT-y-1] = 255
            else:
                if lights[x][WORLD_HEIGHT-y-1] > current_light2:
                    current_light2 = lights[x][WORLD_HEIGHT-y-1]
                elif current_light2 != 0:
                    lights[x][WORLD_HEIGHT-y-1] = current_light2
                if lights[x][WORLD_HEIGHT-y-1] == current_light2 and local_ids[world[x][WORLD_HEIGHT-y-1].id].state == 1:
                    current_light2 -= 25
    for y in xrange(WORLD_HEIGHT):
        current_light = 0
        current_light2 = 0
        for x in xrange(WORLD_WIDTH):
            if local_ids[world[x][y].id].illuminant == 1:
                current_light = 255
                lights[x][y] = 255
            else:
                if lights[x][y] > current_light:
                    current_light = lights[x][y]
                elif current_light != 0:
                    lights[x][y] = current_light
                if lights[x][y] == current_light and local_ids[world[x][y].id].state == 1:
                    current_light -= 25
            if local_ids[world[WORLD_WIDTH-x-1][y].id].illuminant == 1:
                current_light2 = 255
                lights[WORLD_WIDTH-x-1][y] = 255
            else:
                if lights[WORLD_WIDTH-x-1][y] > current_light2:
                    current_light2 = lights[WORLD_WIDTH-x-1][y]
                elif current_light2 != 0:
                    lights[WORLD_WIDTH-x-1][y] = current_light2
                if lights[WORLD_WIDTH-x-1][y] == current_light2 and local_ids[world[WORLD_WIDTH-x-1][y].id].state == 1:
                    current_light2 -= 25
    return lights
                
def drawBlocks(camera):
    x = -(camera.x % 16)
    for i in range(int(math.floor(camera.x/16.0)), int(math.ceil((camera.x + camera.width)/16.0))):
        y = -(camera.y % 16)
        for j in range(int(math.floor(camera.y/16.0)), int(math.ceil((camera.y + camera.height)/16.0))):
            try:
                screen.blit(blockRenders[c.world[i][j].id][255 - c.lights[i][j]],[x,y])
            except:
                screen.blit(blockRenders[0][255 - c.lights[i][j]],[x,y])
            y += 16
        x += 16

 
def drawInventory():
    initial_x = 5 #(WINDOW_WIDTH - 328) / 2
    initial_y = 5 #WINDOW_HEIGHT - 40
    for i in range(len(inv)/inv_row):
        row = i * 36
        screen.blit(inventoryBar, (initial_x, initial_y+row))
    back = pygame.Surface((32,32)).convert()
    back.set_alpha(128)
    back.fill((128,128,128)) 
    for i in range(len(inv)):
        row = i/9 * 36
        mo = i%9
        if inv[i] is not None:
            screen.blit(pygame.transform.scale2x(ids[inv[i]["id"]].image), (initial_x + 32*mo + 4*(mo+1), initial_y+4+row))
            text = str(inv[i]["quantity"])
            text_surf = inv_font.render(text, 1, (0,0,0))
            screen.blit(text_surf, (initial_x + 32*mo + 4*(mo+1) + (32 - inv_font.size(text)[0]), initial_y+4+row))
        else:
            screen.blit(back, (initial_x + 32*mo + 4*(mo+1), initial_y+4+row))
    for i in range(4):
        row = selected/9 * 36
        mo = selected%9
        pygame.draw.rect(screen, (128, 128, 128), (initial_x + 36 * mo + i, initial_y + i + row, 40 - 2*i, 40 - 2*i), 1)

def drawName(name,x,y):
    text_surf = inv_font.render(name, 1, (0,0,0))
    screen.blit(text_surf, (x+8-(text_surf.get_width()/2)-camera.x, y-16-camera.y))
    
def drawHealth(health,x,y):
    health_pixels = int(max(min(health / float(100) * 34, 34), 0))
    pygame.draw.rect(screen, (255,0,0), (x-9-camera.x,y-5-camera.y,34,4))
    pygame.draw.rect(screen, (0,255,0), (x-9-camera.x,y-5-camera.y,health_pixels,4))


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
        if ids[c.world[(char.rect.left + 1) / 16][char.rect.bottom / 16].id].state == 1 or ids[c.world[(char.rect.right - 1) / 16][char.rect.bottom / 16].id].state == 1:
            char.jumping = False
            char.yVel = 0
            return
        else:
            char.jumping = True
            char.yVel += .5
            try:
                if ids[c.world[(char.rect.left + 1) / 16][int((char.rect.bottom + char.yVel) / 16)].id].state == 0 and ids[c.world[(char.rect.right - 1) / 16][int((char.rect.bottom + char.yVel) / 16)].id].state == 0:
                    char.rect.y += char.yVel
                else:
                    char.rect.y += 1
            except:
                char.rect.y += 1
    else:
        if ids[c.world[(char.rect.left + 1) / 16][char.rect.y / 16 + 1].id].state == 1 or ids[c.world[(char.rect.right - 1) / 16][char.rect.y / 16 + 1].id].state == 1:
            char.jumping = False
            char.yVel = 0
            return
        else:
            char.jumping = True
            char.yVel += .5
            if ids[c.world[(char.rect.left + 1) / 16][int((char.rect.y + char.yVel) / 16)].id].state == 0 and ids[c.world[(char.rect.right - 1) / 16][int((char.rect.y + char.yVel) / 16)].id].state == 0:
                char.rect.y += char.yVel
            elif ids[c.world[(char.rect.left + 1) / 16][(char.rect.y - 1) / 16].id].state == 0 and ids[c.world[(char.rect.right - 1) / 16][(char.rect.y - 1) / 16].id].state == 0:
                char.rect.y -= 1


def resetPosition():
    character.rect.topleft = ((WORLD_WIDTH_PX-16)/2, 0) #initial position is in the sky in the middle of the map
    character.rect.x = character.rect.x/16*16
    while not (getId(c.world[(character.rect.left + 1) / 16][character.rect.bottom / 16].id).state == 1 or getId(c.world[(character.rect.right - 1) / 16][character.rect.bottom / 16].id).state == 1):
        character.rect.y += 1 #lower player until they hit ground

#constants
WINDOW_WIDTH = 640 #default value; can be changed in config
WINDOW_HEIGHT = 480 #default value; can be changed in config
TILE_SIZE_X = 16
TILE_SIZE_Y = 16
WORLD_WIDTH_PX = 2048
WORLD_HEIGHT_PX = 2048
WORLD_WIDTH = WORLD_WIDTH_PX/TILE_SIZE_X
WORLD_HEIGHT = WORLD_HEIGHT_PX/TILE_SIZE_Y

if __name__ == "__main__":
    Config = ConfigParser.ConfigParser()
    Config.read("config.ini")
    WINDOW_WIDTH = int(Config.get("display", "width"))
    WINDOW_HEIGHT = int(Config.get("display", "height"))
    
    pygame.init()
    pygame.display.set_caption("Block Fun")
    pygame.display.set_icon(pygame.image.load("images/tiles/grass.png"))
    flags = 0
    fullscreen_option = bool(int(Config.get("display", "fullscreen")))
    if fullscreen_option:
        flags = flags | FULLSCREEN
    screen = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT), flags)
    
    inv_font =  pygame.font.Font(None, 14)
    
    camera = pygame.Rect(0,0,WINDOW_WIDTH,WINDOW_HEIGHT)
    
    ids = [None for i in range(256)]
    
    from id_list import *
    
    sky_tile = Tile(*sky_id)
    invisible_tile = Tile(*invisible_id)
    bedrock_tile = Tile(*bedrock_id)
    grass_tile = Tile(*grass_id)
    dirt_tile = Tile(*dirt_id)
    stone_tile = Tile(*stone_id)
    sand_tile = Tile(*sand_id)
    wood_tile = Tile(*wood_id)
    leaf_tile = Tile(*leaf_id)
    chest_tile = Tile(*chest_id)
    diamond_tile = Tile(*diamond_id)
    torch_tile = Tile(*torch_id)
    
    pistol_item = Id(*pistol_id)
    
    
    inventoryBar =  pygame.image.load("images/bar.png").convert_alpha()
    chestBar = pygame.image.load("images/bar_small.png").convert_alpha()
    
    clock = pygame.time.Clock()
    
    character = Character("images/character.png", "User")
    
    # real_tiles = [ids[i] for i in range(len(ids)) if ids[i] is not None]
    # breakables = [real_tiles[i] for i in range(len(real_tiles)) if real_tiles[i].breakable]
    # breakables.remove(3) #cant get grass because grass drops dirt
    
    inv_row = 9
    inv = [None for i in range(inv_row*2)]
    
    frame = 0
    
    selected = 0
    

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
    updateGrass(c.world) #initial grass update
    
    c.name = name
    c.Send({"action": "name", "name": c.name}) #sends username to server
    
    c.Send({"action": "health", "health": c.health}) #send initial health value
    
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
    
    lightBacks = [lightBack.copy() for i in xrange(256)]
    for i in xrange(len(lightBacks)):
        lightBacks[i].set_alpha(i)
        
    blockRenders = []
    for i in range(len(ids)):
        blockRenders.append([])
        try:
            for j in xrange(256):
                block_copy = ids[i].image.copy()
                block_copy.blit(lightBacks[j], (0,0))
                blockRenders[i].append(block_copy)
        except:
            pass
    
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
        hovered = ids[hovered_data.id]
        
        if key[K_a]:    
            if ids[c.world[(character.rect.left - 1)/16][character.rect.top / 16].id].state == 0 and ids[c.world[(character.rect.left - 1) / 16][(character.rect.bottom - 1) / 16].id].state == 0:
                character.rect.x -= 1
        if key[K_d]:
            if ids[c.world[(character.rect.right + 1)/16][character.rect.top / 16].id].state == 0 and ids[c.world[(character.rect.right + 1) / 16][(character.rect.bottom - 1) / 16].id].state == 0:
                character.rect.x += 1
        if key[K_SPACE]:
            if not character.jumping and (ids[c.world[(character.rect.left + 1) / 16][character.rect.top / 16 - 1].id].state == 0 and ids[c.world[(character.rect.right - 1) / 16][character.rect.top / 16 - 1].id].state == 0):
                character.yVel = -8
                character.jumping = True
                character.rect.y -= 16
        #left click
        if mouse_press[0]:
            if getSlotAmount(selected) != 0 and inv[selected]["id"] == 100:
                #do gun stuff
                if time.time() - c.time_shot >= 0.33:
                    x_distance = mouse_pos[0] + camera.x - character.rect.x
                    y_distance = mouse_pos[1] + camera.y - character.rect.y
                    rotation_angle = math.atan2(y_distance, x_distance)
                    c.Send({"action": "addProjectile", "width": 5, "height": 5, "startpos": character.rect.center, "speed": 10, "traveldistance": 400, "angle": rotation_angle, "color": (0,0,0)})
                    c.time_shot = time.time()
            elif hovered.breakable:
                #addToInv(hovered.drops, 1)
                c.Send({"action": "blockChange", "x": (mouse_pos[0] + camera.x)/16, "y": (mouse_pos[1]+ camera.y)/16, "id": 0, "metadata": None, "inv": hovered.drops, "amount": 1})
                #c.world[(mouse_pos[0] + camera.x)/16][(mouse_pos[1]+ camera.y)/16] = Data(0)
        #right click
        if mouse_press[2]:
            if hovered.id == 0:
                if getSlotAmount(selected) != 0:
                    if ids[inv[selected]["id"]].type == "block":
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
                        selected = len(inv)-1
                    else:
                        selected -= 1
                #scroll down
                elif event.button == 5:
                    if selected == len(inv)-1:
                        selected = 0
                    else:
                        selected += 1
            if event.type == KEYDOWN:
                #chest controls
                if event.key == K_1:
                    if hovered_data.id == 9:
                        if getSlotAmount(0,data=hovered_data.metadata) > 0:
                            hover_id = hovered_data.metadata[0]["id"]
                            addToInv(hover_id,-1,data=hovered_data.metadata)
                            c.Send({"action": "blockChange", "x": (mouse_pos[0] + camera.x)/16, "y": (mouse_pos[1]+ camera.y)/16, "id": hovered_data.id, "metadata": hovered_data.metadata, "inv": hover_id, "amount": 1})
                if event.key == K_2:
                    if hovered_data.id == 9:
                        if getSlotAmount(1,data=hovered_data.metadata) > 0:
                            hover_id = hovered_data.metadata[1]["id"]
                            addToInv(hover_id,-1,data=hovered_data.metadata)
                            c.Send({"action": "blockChange", "x": (mouse_pos[0] + camera.x)/16, "y": (mouse_pos[1]+ camera.y)/16, "id": hovered_data.id, "metadata": hovered_data.metadata, "inv": hover_id, "amount": 1})
                if event.key == K_3:
                    if hovered_data.id == 9:
                        if getSlotAmount(2,data=hovered_data.metadata) > 0:
                            hover_id = hovered_data.metadata[2]["id"]
                            addToInv(hover_id,-1,data=hovered_data.metadata)
                            c.Send({"action": "blockChange", "x": (mouse_pos[0] + camera.x)/16, "y": (mouse_pos[1]+ camera.y)/16, "id": hovered_data.id, "metadata": hovered_data.metadata, "inv": hover_id, "amount": 1})
                if event.key == K_4:
                    if hovered_data.id == 9:
                        if getSlotAmount(3,data=hovered_data.metadata) > 0:
                            hover_id = hovered_data.metadata[3]["id"]
                            addToInv(hover_id,-1,data=hovered_data.metadata)
                            c.Send({"action": "blockChange", "x": (mouse_pos[0] + camera.x)/16, "y": (mouse_pos[1]+ camera.y)/16, "id": hovered_data.id, "metadata": hovered_data.metadata, "inv": hover_id, "amount": 1})
                if event.key == K_5:
                    if hovered_data.id == 9:
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
        drawBlocks(camera)
        pygame.draw.rect(screen, (0,0,0), ((mouse_pos[0] + camera.x ) / 16 * 16 - camera.x, (mouse_pos[1] + camera.y) / 16 * 16 - camera.y, 16, 16), 1)
        for i in range(len(c.players)):
            if c.players[i][2] != c.uuid: #only use server data to draw other players; our player is drawn client side
                screen.blit(character.image, (c.players[i][0]-camera.x,c.players[i][1]-camera.y))
                drawName(c.players[i][3],c.players[i][0],c.players[i][1])
                drawHealth(c.players[i][4],c.players[i][0],c.players[i][1])
        screen.blit(character.image, (character.rect.x - camera.x, character.rect.y - camera.y))
        drawProjectiles(c.projectiles)
        drawName(c.name,character.rect.x,character.rect.y)
        drawHealth(c.health,character.rect.x,character.rect.y)
        if key[K_c]: #chests only show contents if c is held
            if hovered_data.metadata != None:
                drawChest(hovered_data.metadata,(mouse_pos[0] + camera.x)/16*16,(mouse_pos[1]+ camera.y)/16*16)
        drawInventory()
        pygame.display.update()
#         frame += 1
