import pygame as pg
# game options/settings
TITLE = "Py runner"
WIDTH = 480
HEIGHT = 600
FPS = 60
FONT_NAME = 'arial'
HS_FILE = "highscore.txt"
SPRITESHEET = "spritesheet_jumper.png"

# Player properties
PLAYER_ACC = 1.5
PLAYER_FRICTION = -0.2
PLAYER_GRAVITY = 0.8
PLAYER_JUMP = 20

#시작지점
PLATFORM_LIST = [(0, HEIGHT - 60),
                 (WIDTH/2 - 50, HEIGHT*3/4),
                 (125, HEIGHT - 350),
                 (350, 200,),
                 (175, 100,)]

#색깔
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTBLUE = (0, 155, 155)
BGCOLOR = LIGHTBLUE

#볼륨
SFXVOLUME = 1.0
BGMVOLUME = 1.0

#조작키
KEY_LEFT = pg.K_LEFT
KEY_RIGHT = pg.K_RIGHT
KEY_UP = pg.K_UP
KEY_DOWN = pg.K_DOWN
KEY_ENTER = pg.K_RETURN
KEY_JUMP = pg.K_SPACE