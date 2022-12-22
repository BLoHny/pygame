import pygame as pg
from settings import *
from random import choice
import xml.etree.ElementTree as ET
import random
import time
vec = pg.math.Vector2

tree = ET.parse('img/spritesheet_jumper.xml')
root = tree.getroot()
spriteDict : dict = {}
for child in root:
    spriteDict[child.get('name')] = [child.get('x'), child.get('y'), child.get('width'), child.get('height')]
class Spritesheet:
    # Utility class for loading spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        # Grab an image out of a lager spritesheet
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, (width//2, height//2))
        return image


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game

        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0

        self.load_images()
        self.image = self.standing_frames[0]

        self.rect = self.image.get_rect()
        self.rect.center = (40, HEIGHT - 100)

        self.pos = vec(40, HEIGHT - 100)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def load_images(self):
        self.standing_frames = [self.game.spritesheet.get_image(614, 1063, 120, 191),
                                self.game.spritesheet.get_image(690, 406, 120, 201)]
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)

        self.walk_frames_r = [self.game.spritesheet.get_image(678, 860, 120, 201),
                              self.game.spritesheet.get_image(692, 1458, 120, 207)]
        for frame in self.walk_frames_r:
            frame.set_colorkey(BLACK)

        self.walk_frames_l = [pg.transform.flip(frame, True, False)
                              for frame in self.walk_frames_r]

        self.jump_frame = self.game.spritesheet.get_image(382, 763, 150, 181)
        self.jump_frame.set_colorkey(BLACK)

    def jump_cut(self):
        if self.jumping:
            if self.vel.y < -3:
                self.vel.y = -3

    def jump(self):
        # jump only if standing on a platform
        # self.rect.y += 0.1
        # hits = pg.sprite.spritecollide(self, self.game.platforms, False)
        # self.rect.y -= 0.1
        if not self.jumping:
            self.jumping = True
            self.vel.y = -PLAYER_JUMP
            return True
        return False

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAVITY)
        keys = pg.key.get_pressed()

        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        self.acc.x += self.vel.x*PLAYER_FRICTION
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.5*self.acc

        if self.pos.x > WIDTH + self.rect.width/2:
            self.pos.x = 0 - self.rect.width/2
        if self.pos.x < 0 - self.rect.width/2:
            self.pos.x = WIDTH + self.rect.width/2

        self.rect.midbottom = self.pos

    def animate(self):
        now = pg.time.get_ticks()

        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False

        if self.walking:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = ((self.current_frame + 1)
                                      % len(self.walk_frames_l))

                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                else:
                    self.image = self.walk_frames_l[self.current_frame]
                    self.rect = self.image.get_rect()
                    self.rect.bottom = bottom

        if not self.jumping and not self.walking:
            if (now - self.last_update) > 350:
                self.last_update = now
                self.current_frame = ((self.current_frame + 1)
                                      % len(self.standing_frames))
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom


class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self)
        self.game = game

        images = []
        item_images = []
        v = spriteDict["ground_grass.png"]
        images.append(self.game.spritesheet.get_image(int(v[0]), int(v[1]), int(v[2]), int(v[3])))
        v = spriteDict["ground_grass_small.png"]
        images.append(self.game.spritesheet.get_image(int(v[0]), int(v[1]), int(v[2]), int(v[3])))
        
        test_item = random.randrange(0, 20)

        self.image = choice(images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
            

class MovingYPlatform(Platform):
    startY = 0
    endY = 0
    speed = 0
    def __init__(self, game, x, startY, endY, speed):
        pg.sprite.Sprite.__init__(self)
        self.game = game

        images = []
        v = spriteDict['spring_out.png']
        images.append(self.game.spritesheet.get_image(int(v[0]), int(v[1]), int(v[2]), int(v[3])))
        v = spriteDict['grass_brown1.png']
        images.append(self.game.spritesheet.get_image(int(v[0]), int(v[1]), int(v[2]), int(v[3])))

        self.image = choice(images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = startY - 1
        self.startY = startY
        self.endY = endY
        self.speed = speed
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y <= self.endY:
            self.rect.y = self.endY
            self.speed = -self.speed
        if self.rect.y >= self.startY:
            self.rect.y = self.startY
            self.speed = -self.speed
            
class MovingPlatform(Platform):
    startX = 0
    endX = 0
    speed = 0
    def __init__(self, game, startX, endX, y, speed):
        pg.sprite.Sprite.__init__(self)
        self.game = game

        images = []
        v = spriteDict['spring_out.png']
        images.append(self.game.spritesheet.get_image(int(v[0]), int(v[1]), int(v[2]), int(v[3])))
        v = spriteDict['grass_brown1.png']
        images.append(self.game.spritesheet.get_image(int(v[0]), int(v[1]), int(v[2]), int(v[3])))

        self.image = choice(images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = startX + 1
        self.startx = startX
        self.endX = endX
        self.rect.y = y
        self.speed = speed
    def update(self):
        self.rect.x += self.speed
        if self.rect.x >= self.endX:
            self.rect.x = self.endX
            self.speed = -self.speed
        if self.rect.x <= self.startX:
            self.rect.x = self.startX
            self.speed = -self.speed
            
class item(Platform):
    def __init__(self, game,x, y):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        
        item_images = []
        v = spriteDict["silver_1.png"]
        item_images.append(self.game.spritesheet.get_image(int(v[0], int(v[1]), int(v[2]), int(v[3]))))
        
        self.image = choice(item_images)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    def update(self):
        if self.rect.x >= self.endX:
            self.rect.x = self.endX
            self.speed = -self.speed
        if self.rect.x <= self.startX:
            self.rect.x = self.startX
            self.speed = -self.speed

class BrokenPlatform(Platform):
    genTime = 2147483647
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self)
        self.game = game

        images = []
        v = spriteDict["ground_grass_broken.png"]
        images.append(self.game.spritesheet.get_image(int(v[0]), int(v[1]), int(v[2]), int(v[3])))
        v = spriteDict["ground_grass_small_broken.png"]
        images.append(self.game.spritesheet.get_image(int(v[0]), int(v[1]), int(v[2]), int(v[3])))

        self.image = choice(images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def update(self):
        if time.time() - self.genTime > 0.67:
            return True
        return False