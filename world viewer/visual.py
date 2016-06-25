import pygame, ast, sys
import pygame._view
from pygame.locals import *

world_file = open("world data server gen.txt")
world = ast.literal_eval(world_file.readlines()[0].strip("\n"))
pygame.init()
pygame.display.set_caption("Visual of World")
pygame.display.set_icon(pygame.image.load("images/tiles/grass.png"))
screen = pygame.display.set_mode((896,896))

id_to_image = {
 0: pygame.transform.scale(pygame.image.load("images/tiles/sky.png").convert(), (14, 14)),
 1: pygame.transform.scale(pygame.image.load("images/tiles/invisible.png").convert(), (14, 14)),
 2: pygame.transform.scale(pygame.image.load("images/tiles/bedrock.png").convert(), (14, 14)),
 3: pygame.transform.scale(pygame.image.load("images/tiles/grass.png").convert(), (14, 14)),
 4: pygame.transform.scale(pygame.image.load("images/tiles/dirt.png").convert(), (14, 14)),
 5: pygame.transform.scale(pygame.image.load("images/tiles/stone.png").convert(), (14, 14)),
 6: pygame.transform.scale(pygame.image.load("images/tiles/sand.png").convert(), (14, 14)),
 7: pygame.transform.scale(pygame.image.load("images/tiles/wood.png").convert(), (14, 14)),
 8: pygame.transform.scale(pygame.image.load("images/tiles/leaf.png").convert(), (14, 14))
}

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
    
    for i in range(64):
        for j in range(64):
            screen.blit(id_to_image[world[i][j]], (j*14,i*14))
    
    pygame.display.update()
