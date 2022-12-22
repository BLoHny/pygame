import pygame as pg
import random
from settings import *
from sprites import *
from os import path

a = 1

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

    def load_data(self):
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'img')

        try:
            with open(path.join(self.dir, HS_FILE), 'r') as f:
                self.highscore = int(f.read())
        except FileNotFoundError:
            self.highscore = 0

        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))

        self.snd_dir = path.join(self.dir, 'snd')
        self.gameover_sound = pg.mixer.Sound(
            path.join(self.snd_dir, 'game_over.wav'))

    def new(self):
        self.score = 0
        self.all_sprites = pg.sprite.Group()
        self.platforms = []

        self.player = Player(self)
        self.player.rect.x = WIDTH / 2 - 50
        self.all_sprites.add(self.player)

        for plat in PLATFORM_LIST:
            p = Platform(self, *plat)
            self.all_sprites.add(p)
            self.platforms.append(p)

        pg.mixer.music.load(path.join(self.snd_dir, 'happytune.mp3'))

        self.run()

    def run(self):
        # Game Loop
        pg.mixer.music.play(-1)
        self.playing = True

        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

        pg.mixer.music.fadeout(500)

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()
        # check if player hits a platfrom
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.y < lowest.rect.centery:
                    self.player.pos.y = lowest.rect.top + 0.1
                    self.player.vel.y = 0
                    self.player.jumping = False
                    if type(lowest) is BrokenPlatform:
                        lowest.kill()
                        list.remove(self.platforms, lowest)
                    

        # If player reached top 1/4 of screen
        if self.player.rect.top <= HEIGHT/4:
            self.player.pos.y += max(abs(self.player.vel.y), 5)
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 5)
                if type(plat) is MovingYPlatform:
                    plat.startY += max(abs(self.player.vel.y), 5)
                    plat.endY += max(abs(self.player.vel.y), 5)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    list.remove(self.platforms, plat)
                    # self.score += 10

        # Die
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if type(sprite) is MovingYPlatform:
                    sprite.startY -= max(abs(self.player.vel.y), 5)
                    sprite.endY -= max(abs(self.player.vel.y), 5)
                if sprite.rect.bottom < 0:
                    sprite.kill()
                    list.remove(self.platforms, sprite)
        if len(self.platforms) <= 0:
            self.playing = False

        # Spawn new platforms
        pListLen = len(self.platforms)
        pList = self.platforms

        while pListLen is not 0 and self.player.rect.bottom - pList[pListLen - 1].rect.top < 240:
            width = random.randrange(50, 100)
            if random.randrange(0, 10) <= int(self.score / 200):
                if random.randrange(0, 2) == 0 and self.score >= 1000:
                    startY = pList[pListLen - 1].rect.top - random.randrange(
                        50 + min(int(self.score / 10), 189), 240)
                    p = MovingYPlatform(self, random.randrange(0, WIDTH - width),
                                        startY, startY - random.randrange(100 + min(int(self.score / 10), 189), 300), random.randrange(2, 4))
                else:
                    startX = random.randrange(0, WIDTH - width - 30)
                    p = MovingPlatform(self, startX, random.randrange(startX + 10, WIDTH - width),
                                   pList[pListLen - 1].rect.top - random.randrange(50 + min(int(self.score / 10), 189), 240), random.randrange(2, 4 + int(self.score / 500)))

            else:
                p = Platform(self, random.randrange(0, WIDTH - width), pList[pListLen - 1].rect.top - random.randrange(
                    50 + min(int(self.score / 10), 189), 240))
            self.platforms.append(p)
            self.all_sprites.add(p)
            pListLen = len(pList)
            pList = self.platforms
            self.score += 10

        for platform in self.platforms:
            if type(platform) is MovingPlatform:
                platform.update()
            if type(platform) is MovingYPlatform:
                platform.update()

    def events(self):
        # Game Loop - Events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.player.jump_cut()

    def draw(self):
        if self.platforms.__len__() > 0:
            fet = self.platforms.pop()
        else:
            fet = Platform(self, 0, 0)
        self.platforms.append(fet)
        # Game Loop - Draw
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)
        self.draw_text(str(self.score), 22, WHITE, WIDTH/2, 15)
        self.draw_text("player y" +
                       str(self.player.rect.y), 22, WHITE, WIDTH/2, 40)
        self.draw_text("player x" +
                       str(self.player.rect.x), 22, WHITE, WIDTH/2, 40 + 25)
        self.draw_text("y of last appended platform" +
                       str(fet.rect.y), 22, WHITE, WIDTH/2, 65 + 25)
        self.draw_text("x of last appended platform" +
                       str(fet.rect.x), 22, WHITE, WIDTH/2, 90 + 25) 
        self.draw_text("" + str(pg.sprite.spritecollide(self.player, self.platforms, False)), 22, WHITE, WIDTH/2, 115 + 25)

        # *after* drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self):
        # game splash/start screen
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 48, WHITE, WIDTH/2, HEIGHT/4)
        self.draw_text("Arrows to move, Space to jump",
                       22, WHITE, WIDTH/2, HEIGHT/2)
        self.draw_text("Press a key to play",
                       22, WHITE, WIDTH/2, HEIGHT*3/4)
        self.draw_text("High Score : " + str(self.highscore),
                       22, WHITE, WIDTH/2, 15)
        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        # game over/continue
        if not self.running:
            return
        self.screen.fill(BGCOLOR)
        self.gameover_sound.play()

        self.draw_text("GAME OVER", 48, WHITE, WIDTH/2, HEIGHT/4)
        self.draw_text("Score : " + str(self.score),
                       22, WHITE, WIDTH/2, HEIGHT/2)
        self.draw_text("Press a key to play again",
                       22, WHITE, WIDTH/2, HEIGHT*3/4)

        if self.score > self.highscore:
            self.gameover_sound.play()
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE!",
                           22, WHITE, WIDTH/2, HEIGHT/2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.gameover_sound.play()
            self.draw_text("High Score : " + str(self.highscore),
                           22, WHITE, WIDTH/2, 15)

        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
