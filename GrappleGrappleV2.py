import pygame as pg
from pygame.locals import *
from sys import exit

import math

pg.init()
pg.font.init()

#Font Initialisation
text = pg.font.SysFont('Comic Sans MS', 30)

#Clock Initialisation
clock = pg.time.Clock()
prevT = 0

#Screen Initialisation
screenObjects = []
screenWidth = 800
screenHeight = 600
screen = pg.display.set_mode((screenWidth, screenHeight))
pg.display.set_caption("Grapple Grapple v2")
screen.fill((0,0,0))

#Physics Variables
DAMPING = 1
HOOKDAMPING = 0.005
HOOKBASELENGTH = 100
GRAVITY = 800
SPEED = 500
JUMP = 500
xVel = 0
yVel = 0
speed = 3600
hooking = False
touchingGround = False

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

class polygon(object):
    def move(self,xOffset,yOffset):
        for a in range(len(self.params[2])):
            self.params[2][a][0] += xOffset
            self.params[2][a][1] += yOffset
    def goto(self,x,y):
        xOffset = x - self.params[2][0][0]
        yOffset = y - self.params[2][0][1]
        self.move(xOffset, yOffset)

    def getCoords(self):
        return(self.params[2][0])

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
#'Polygon': Canvass Colour(a,b,c), points...

#Screen Rendering
def renderScreen(objects):
    screen.fill((0,0,0))

    pg.draw.rect(screen, (255,255,255), [100,50,600,500], 1)
    for object in objects:
        if object.shape == 'line' and hooking:
            pg.draw.line(object.canvas, object.colour, object.pos1, object.pos2, object.width)
        if object.shape == 'rect':
            pg.draw.rect(object.params[0], object.params[1], centralise(object.params[2]))
        if object.shape == 'circle':
            pg.draw.circle(object.params[0], object.params[1],object.params[2],object.params[3])
        if object.shape == 'polygon':
            pg.draw.polygon(object.params[0], object.params[1], object.params[2])
    screen.blit(text.render('Score: ' + str(score), False, (255,255,255)), (0,0))
    if speeding:
        screen.blit(text.render('Speeding Up!', False, (255, 0, 0)), (400, 300))

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
    magnitude = math.ceil(math.sqrt(xDifference ** 2 + yDifference ** 2) * deltaTime)
    if HOOKBASELENGTH**2 > xDifference**2 + yDifference**2:
        xDifference, yDifference = 0, 0
    xDifference, yDifference = math.cbrt(xDifference), math.cbrt(yDifference)
    if hookCoords[0] < playerCoords[0]:
        xDifference *= -1
    if hookCoords[1] < playerCoords[1]:
        yDifference *= -1
    xDifference /= HOOKDAMPING
    yDifference /= HOOKDAMPING
    hookLine.updateWidth((1+magnitude))
    xVel += xDifference*deltaTime
    yVel += yDifference*deltaTime
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

def enemyMovement(enemyPos, playerPos):
    xOffset = -enemyPos[0] + playerPos[0]
    yOffset = -enemyPos[1] + playerPos[1]
    if xOffset != 0:
        xYRatio = yOffset/xOffset
    else:
        xYRatio = yOffset/0.0001
    xTransform = math.sqrt(speed/((xYRatio**2)+1)) * deltaTime
    if xOffset < 0:
        xTransform *= -1
    yTransform = xYRatio * xTransform
    return xTransform, yTransform

def speedUp(speed):
    return speed + 600

def endGame():
    score = 0
    speed = 0.01
    print('You lost', player.getCoords())
    player.goto(30,30)
    enemy.goto(400,300)
#Line Initialisation
hookLine = line('line', screen, (255, 0, 255), [0,0], [0,0], 10)
screenObjects.append(hookLine)

#Player Initialisation
player = object('rect', screen, (255, 255, 0), [30,30,10,10])
screenObjects.append(player)

#HookNode Initialisation
hookNode = object('circle', screen, (255, 255, 255),[400,300],10)
screenObjects.append(hookNode)

#Enemy Initialisation
enemy = polygon('polygon', screen, (100, 50, 135), [[40,30],[60,40],[50,30],[60,20]])
screenObjects.append(enemy)

enemy.goto(400,300)

#Game loop
score = 0
tAtLastLoss = 0
while True:
    t = pg.time.get_ticks()
    clock.tick(60)
    #Sort out the delta time for FPS normalisation
    #deltaTime = 1/60
    deltaTime = (t-prevT)/1000
    prevT = t

    score = (t - tAtLastLoss) // 100

    if score % 100 <= 2 and score > 2:
        speeding = True
        speed = speedUp(speed)
    else:
        speeding = False
    
    #Input handling
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()
        if event.type == pg.MOUSEBUTTONDOWN:
            hooking= True
        if event.type == pg.MOUSEBUTTONUP:
            hooking=False
        updateNode(pg.mouse.get_pos())

    pressed = pg.key.get_pressed()
    move = [move_map[key] for  key in move_map if pressed[key]]
    if 'up' in move and touchingGround:
        touchingGround = False
        yVel = -JUMP
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

    if hooking:
        xVel, yVel = hookPull(xVel, yVel, player.getCoords(), hookNode.getCoords())

    player.move(xVel*deltaTime,yVel*deltaTime)

    #Border Handling
    if player.getCoords()[1] + (yVel*deltaTime) < 550:
        yVel += (GRAVITY*deltaTime)
        touchingGround = False
    else:
        yVel = 0
        player.goto(player.getCoords()[0], 550)
        touchingGround = True
    if player.getCoords()[1] + (yVel*deltaTime) < 50:
        yVel = 0
        player.goto(player.getCoords()[0], 50)
    if player.getCoords()[0] + (xVel*deltaTime) > 700:
        xVel = 0
        player.goto(700, player.getCoords()[1])
    if player.getCoords()[0] + (xVel*deltaTime) < 100:
        xVel = 0
        player.goto(100, player.getCoords()[1])

    #Update Line
    playerPos = player.getCoords()
    hookPos = hookNode.getCoords()
    hookLine.goto(playerPos, hookPos)

    #Move Enemy
    enemy.move(enemyMovement(enemy.getCoords(), player.getCoords())[0], enemyMovement(enemy.getCoords(), player.getCoords())[1])

    #Collision Testing
    mpos = pg.mouse.get_pos()
    playerHitbox = pg.draw.rect(screen,(0,0,0) , (player.getCoords()[0],player.getCoords()[1], 10, 10))
    enemyHitbox = pg.draw.circle(screen, (0,0,0) ,(enemy.getCoords()[0], enemy.getCoords()[1]), 10)
    if playerHitbox.colliderect(enemyHitbox):
        endGame()
        tAtLastLoss = pg.time.get_ticks()

    renderScreen(screenObjects)