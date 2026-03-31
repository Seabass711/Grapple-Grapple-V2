import pygame as pg
from pygame.locals import *
from sys import exit

pg.init()

#Clock Initialisation
clock = pg.Clock
prevT = 0

#Screen Initialisation
screenObjects = []
screenWidth = 800
screenHeight = 600
screen = pg.display.set_mode((screenWidth, screenHeight))
pg.display.set_caption("Grapple Grapple v2")
screen.fill((255,0,0))

#Physics Variables
DAMPING = 10
GRAVITY = 5
SPEED = 3
JUMP = 0.4
xVel = 0
yVel = 0

#Movemap courtesy of stack overflow
move_map = {pg.K_w: 'up',
            pg.K_s: 'down',
            pg.K_a: 'left',
            pg.K_d: 'right'}

class object():
    def __init__(self, shape, *params):
        self.shape = shape
        self.params = params
    def move(self, x, y):
        self.params[2][0] += x
        self.params[2][1] += y
    def goto(self, x, y):
        self.params[2][0] = x
        self.params[2][1] = y
    def getCoords(self):
        return(self.params[2][0],self.params[2][1])

#'Objects' to be written in form [shape, paramaters]
#'Square': Canvas, Colour(a,b,c), Positon and Dimensions(a,b,c,d)

def renderScreen(objects):
    screen.fill((255,0,0))
    for object in objects:
        if object.shape == 'rect':
            pg.draw.rect(object.params[0], object.params[1],tuple(object.params[2]))
    pg.display.update()

player = object('rect', screen, (255, 255, 0), [30,30,10,10])
screenObjects.append(player)

while True:
    #Sort out the delta time for FPS normalisation
    t = pg.time.get_ticks()
    deltaTime = (t-prevT)/1000
    prevT = t
    
    #Input handling
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()
    pressed = pg.key.get_pressed()
    move = [move_map[key] for  key in move_map if pressed[key]]
    if 'up' in move:
        yVel = -JUMP
    if 'down' in move:
        #yVel += 10*deltaTime
        pass
    if 'left' in move:
        xVel -= SPEED*deltaTime
    if 'right' in move:
        xVel += SPEED*deltaTime
    
    #Physics Handling
    xVel *= 1-(DAMPING*deltaTime)
    yVel *= 1-(DAMPING*deltaTime) #This would be for top-down/zero gravity. Here, it acts as 'air resistance'
    player.move(xVel,yVel)
    if (player.getCoords())[1] + yVel < 550:
        yVel += (GRAVITY*deltaTime)
    else:
        yVel = 0
        player.goto((player.getCoords())[0], 550)
    renderScreen(screenObjects)
