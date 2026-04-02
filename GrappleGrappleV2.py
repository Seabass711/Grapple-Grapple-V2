import pygame as pg
from pygame.locals import *
from sys import exit

import math

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
screen.fill((0,0,0))

#Physics Variables
DAMPING = 10
HOOKDAMPING = 1000
HOOKBASELENGTH = 100
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

class line(object):
    def __init__(self, shape, canvas, colour, pos1, pos2, width):
        self.shape = shape
        self.canvas = canvas
        self.colour = colour
        self.pos1 = pos1
        self.pos2 = pos2
        self.width = width
    def move(self, vel1, vel2):
        self.pos1 += vel1
        self.pos2 += vel2
    def goto(self, pos1, pos2):
        self.pos1 = pos1
        self.pos2 = pos2
    def getCoords(self):
        return(self.pos1, self.pos2)
    def updateWidth(self, newWidth):
        self.width = newWidth

#'Objects' to be written in form [shape, paramaters]
#'Square': Canvas, Colour(a,b,c), Positon and Dimensions[x,y,w,h]
#'Circle': Canvas, Colour(a,b,c), position[x,y], radius(r)
#'Line': Canvas, Colour(a,b,c), pos1[x,y], pos2[x,y], width

#Screen Rendering
def renderScreen(objects):
    screen.fill((0,0,0))
    pg.draw.rect(screen, (255,255,255), [100,50,600,500], 1)
    for object in objects:
        if object.shape == 'line':
            pg.draw.line(object.canvas, object.colour, object.pos1, object.pos2, object.width)
        if object.shape == 'rect':
            pg.draw.rect(object.params[0], object.params[1], centralise(object.params[2]))
        if object.shape == 'circle':
            pg.draw.circle(object.params[0], object.params[1],object.params[2],object.params[3])

    pg.display.update()

#Node Updating
def updateNode(position):
    mouseX = position[0]
    mouseY = position[1]
    hookNode.goto(mouseX,mouseY)

#Node & Player Physics
def hookPull(xVel,yVel, playerCoords, hookCoords):
    xDifference = abs(hookCoords[0] - playerCoords[0])
    yDifference = abs(hookCoords[1] - playerCoords[1])
    magnitude = math.ceil(math.sqrt(xDifference ** 2 + yDifference ** 2) / HOOKDAMPING * 10)
    if HOOKBASELENGTH**2 > xDifference**2 + yDifference**2:
        xDifference, yDifference = 0, 0
    xDifference, yDifference = math.cbrt(xDifference), math.cbrt(yDifference)
    if hookCoords[0] < playerCoords[0]:
        xDifference *= -1
    if hookCoords[1] < playerCoords[1]:
        yDifference *= -1
    xDifference /= HOOKDAMPING
    yDifference /= HOOKDAMPING
    hookLine.updateWidth(1+magnitude)
    xVel += xDifference
    yVel += yDifference
    return xVel, yVel

#Normalise playerPos to its centre, (0,0)
def centralise(list):
    x = list[0]
    y = list[1]
    width = list[2]
    height = list[3]
    posX = x - width/2
    posY = y - height/2
    return posX, posY, width, height

#Line Initialisation
hookLine = line('line', screen, (255, 0, 255), [0,0], [0,0], 10)
screenObjects.append(hookLine)

#Player Initialisation
player = object('rect', screen, (255, 255, 0), [30,30,10,10])
screenObjects.append(player)

#HookNode Initialisation
hookNode = object('circle', screen, (255, 255, 255),[400,300],10)
screenObjects.append(hookNode)


#Game loop
while True:
    #Sort out the delta time for FPS normalisation
    t = pg.time.get_ticks()
    deltaTime = (t-prevT)/1000
    prevT = t
    
    #Input handling
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()
        if event.type == pg.MOUSEBUTTONDOWN:
            pass
        updateNode(pg.mouse.get_pos())

    pressed = pg.key.get_pressed()
    move = [move_map[key] for  key in move_map if pressed[key]]
    if 'up' in move:
        #yVel = -JUMP
        pass
    if 'down' in move:
        #yVel += 10*deltaTime
        pass
    if 'left' in move:
        xVel -= SPEED*deltaTime
        pass
    if 'right' in move:
        xVel += SPEED*deltaTime
        pass

    #Physics Handling, could be its own function?
    xVel *= 1-(DAMPING*deltaTime)
    yVel *= 1-(DAMPING*deltaTime) #This would be for top-down/zero gravity. Here, it acts as 'air resistance'

    xVel, yVel = hookPull(xVel, yVel, player.getCoords(), hookNode.getCoords())

    player.move(xVel,yVel)

    #Border Handling
    if player.getCoords()[1] + yVel < 550:
        yVel += (GRAVITY*deltaTime)
    else:
        yVel = 0
        player.goto(player.getCoords()[0], 550)
    if player.getCoords()[1] + yVel < 50:
        yVel = 0
        player.goto(player.getCoords()[0], 50)
    if player.getCoords()[0] + xVel > 700:
        xVel = 0
        player.goto(700, player.getCoords()[1])
    if player.getCoords()[0] + xVel < 100:
        player.goto(100, player.getCoords()[1])

    #Update Line
    playerPos = player.getCoords()
    hookPos = hookNode.getCoords()
    hookLine.goto(playerPos, hookPos)

    renderScreen(screenObjects)