import sys, random, ConfigParser, math
import cPickle as pickle
from time import sleep
from weakref import WeakKeyDictionary
from uuid import uuid4

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

class Data:
    def __init__(self, id, metadata=None):
        self.id = id
        self.metadata = metadata
        if self.id == 9 and self.metadata == None:
            self.metadata = [None for i in range(5)]
            

class Projectile:
    def __init__(self, width, height, startpos, speed, traveldistance, angle, color):
        self.width = width
        self.height = height
        self.color = color
        self.startpos = startpos
        self.rect.topleft = startpos
        self.distance = 0
        self.speed = speed
        self.traveldistance = traveldistance
        self.angle = angle
        
    def rad_to_offset(self, radians, offset):
        x = math.cos(radians) * offset
        y = math.sin(radians) * offset
        return [x, y]
    
    def add(self, u, v):
        return [u[i]+v[i] for i in range(len(u))]
        
    def update(self):
        if self.distance >= self.traveldistance:
            self.kill()
        
        moveamount = self.rad_to_offset(self.angle, self.speed)
        self.rect.topleft = self.add(self.rect.topleft, moveamount)
        self.distance = math.sqrt(math.fabs(self.startpos[0] - self.rect.x) ** 2 + math.fabs(self.startpos[1] - self.rect.y) ** 2)


def generateWorld():
    world = []
    for x in range(WORLD_WIDTH):
        world.append([])
        for y in range(WORLD_HEIGHT):
            world[x].append(Data(0))
    for x in range(WORLD_WIDTH):
        for y in range(WORLD_HEIGHT):
            if x == 0 or x == WORLD_WIDTH - 1:
                world[x][y] = Data(1)
            elif y == 0:
                world[x][y] = Data(1)
            elif y == WORLD_HEIGHT - 1:
                world[x][y] = Data(2)
            elif y >= 0.7 * WORLD_HEIGHT:
                world[x][y] = Data(5)
            elif y >= 0.6 * WORLD_HEIGHT:
                world[x][y] = Data(4)
            else:
                world[x][y] = Data(0)
    for x in range(WORLD_WIDTH):
        for y in range(WORLD_HEIGHT):
            if x > 0 and y < WORLD_HEIGHT - 1 and y > 5 and world[x][y].id != 1 and world[x][y].id != 2:
                if world[x - 1][y + 1].id == 4 and random.random() >= 0.6:
                    world[x][y] =  Data(4)
                if world[x - 1][y - 1].id == 4 and random.random() >= 0.6:
                    world[x][y] =  Data(4)
                if world[x][y - 1].id == 4 and world[x][y].id == 0:
                    world[x][y] =  Data(4)
                if world[x - 1][y + 1].id == 5 and random.random() >= 0.8:
                    world[x][y] =  Data(5)
                if world[x - 1][y - 1].id == 5 and random.random() >= 0.8:
                    world[x][y] =  Data(5)
                if world[x][y - 1].id == 5 and world[x][y].id == 4:
                    world[x][y] =  Data(5)
    for x in range(WORLD_WIDTH):
        for y in range(WORLD_HEIGHT):
            if y >= (WORLD_HEIGHT*7/8) and world[x][y].id == 5 and random.random() >= 0.99:
                world[x][y] =  Data(10)
    
    updateGrass(world)
    for x in range(WORLD_WIDTH):
        for y in range(WORLD_HEIGHT):
            if world[x][y].id == 3 and world[x][y - 1].id == 0 and x > 2 and x < WORLD_WIDTH - 3 and y > 5 and random.random() >= 0.7:
                generateTree(x, y - 1, world, random.randint(3, 8))
    return world

def generateTree(x, y, world, height):

    for i in range(1, height):
        if not world[x][y - i].id == 0:
            return
    if (world[x - 1][y - (height - 1)].id == 0 and world[x + 1][y - (height - 1)].id == 0 and world[x - 2][y - (height)].id == 0 and
            world[x - 1][y - (height)].id == 0 and world[x][y - (height)].id == 0 and world[x + 1][y - (height)].id == 0 and
            world[x + 2][y - (height)].id == 0 and world[x - 1][y - (height + 1)].id == 0 and world[x][y - (height + 1)].id == 0 and
            world[x + 1][y - (height + 1)].id == 0 and world[x][y - (height + 2)].id == 0):
        
        for i in range(height):
            world[x][y - i] = Data(7)
        world[x - 1][y - (height - 1)] = Data(8)
        world[x + 1][y - (height - 1)] = Data(8)
        world[x - 2][y - (height)] = Data(8)
        world[x - 1][y - (height)] = Data(8)
        world[x][y - (height)] = Data(8)
        world[x + 1][y - (height)] = Data(8)
        world[x + 2][y - (height)] = Data(8)
        world[x - 1][y - (height + 1)] = Data(8)
        world[x][y - (height + 1)] = Data(8)
        world[x + 1][y - (height + 1)] = Data(8)
        world[x][y - (height + 2)] = Data(8)
        
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

class ClientChannel(Channel):
    """
    This is the server representation of a single connected client.
    """
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
        self.Send({"action":"world","world":pickle.dumps(self._server.world)})
        self.pos = [0,0]
        self.uuid = uuid4().hex
        self.Send({"action":"uuid","uuid":self.uuid})
        self.name = ""
    
    def Close(self):
        self._server.DelPlayer(self)
    
    ##################################
    ### Network specific callbacks ###
    ##################################
   
    def Network_blockChange(self, data):
        if self._server.world[data["x"]][data["y"]].__dict__ != Data(data["id"], metadata=data["metadata"]).__dict__:
            self._server.world[data["x"]][data["y"]] = Data(data["id"], metadata=data["metadata"])
            self.Send({"action": "addToInv", "id": data["inv"], "amount": data["amount"]})
            self._server.SendToAll({"action": "blockChange", "x": data["x"], "y": data["y"], "id": data["id"], "metadata": data["metadata"]})
    
    def Network_posChange(self, data):
        self.pos = [data["x"],data["y"]]
        self._server.SendToAll({"action": "players", "players": [p.pos+[p.uuid]+[p.name] for p in self._server.players]})
    
    def Network_name(self, data):
        self.name = data["name"]

class GameServer(Server):
    channelClass = ClientChannel
    
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.world = generateWorld()
        self.players = WeakKeyDictionary()
        print 'Server launched'
    
    def Connected(self, channel, addr):
        self.AddPlayer(channel)
    
    def AddPlayer(self, player):
        print "New Player" + str(player.addr)
        self.players[player] = True
        print "players", [p for p in self.players]
    
    def DelPlayer(self, player):
        print "Deleting Player" + str(player.addr)
        del self.players[player]

    
    def SendToAll(self, data):
        [p.Send(data) for p in self.players]
    
    def Launch(self):
        while True:
            self.Pump()
            sleep(0.00001)

TILE_SIZE_X = 16
TILE_SIZE_Y = 16
WORLD_WIDTH_PX = 2048
WORLD_HEIGHT_PX = 2048
WORLD_WIDTH = WORLD_WIDTH_PX/TILE_SIZE_X
WORLD_HEIGHT = WORLD_HEIGHT_PX/TILE_SIZE_Y

if __name__ == "__main__":
    Config = ConfigParser.ConfigParser()
    Config.read("config.ini")
    ip = Config.get("connection", "ip")
    port = int(Config.get("connection", "port"))
    
    s = GameServer(localaddr=(ip, port))
    s.Launch()


