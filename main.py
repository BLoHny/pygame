import pygame as pg
import random
from settings import *
from sprites import *
from os import path
import time
import sys

DEBUG = False
b = True

a = 1
draw_background = pg.image.load("res/img/draw_backgroud.png")
draw_background = pg.transform.scale(draw_background, (480, 600))
start_background = pg.image.load("res/img/start_background.jpg")
start_background = pg.transform.scale(start_background, (480, 600))

end_background = pg.image.load("res/img/end_background.jpg")
end_background = pg.transform.scale(end_background, (480, 600))


class UIModule:
    x = 0
    y = 0
    text = "default text"
    color = WHITE
    fontSize = 22

    def __init__(self, inX, inY, inText, inColor, inFontSize):
        self.x = inX
        self.y = inY
        self.text = inText
        self.color = inColor
        self.fontSize = inFontSize


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
        img_dir = path.join(self.dir, 'res/img')

        try:
            with open(path.join(self.dir, HS_FILE), 'r') as f:
                self.highscore = int(f.read())
        except FileNotFoundError:
            self.highscore = 0

        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))

        self.snd_dir = path.join(self.dir, 'res/snd')
        self.gameover_sound = pg.mixer.Sound(
            path.join(self.snd_dir, 'game_over.wav'))
        self.jump_sound = pg.mixer.Sound(
            path.join(self.snd_dir, 'jumpSound.wav'))
        self.gameover_sound.set_volume(SFXVOLUME)
        self.jump_sound.set_volume(SFXVOLUME)

    def new(self):
        self.score = 0
        self.all_sprites = pg.sprite.Group()
        self.platforms = []
        self.cList = []
        self.tList = []

        self.player = Player(self)
        self.player.rect.x = WIDTH / 2 - 50
        self.all_sprites.add(self.player)

        for plat in PLATFORM_LIST:
            p = Platform(self, *plat)
            self.all_sprites.add(p)
            self.platforms.append(p)

        pg.mixer.music.load(path.join(self.snd_dir, 'happytune.mp3'))
        pg.mixer.music.set_volume(BGMVOLUME)

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
        if self.score < 0:
            self.score = 0
        mhits = []

        # Game Loop - Update
        # update special platforms
        for platform in self.platforms:
            if type(platform) is MovingPlatform:
                platform.update()
            if type(platform) is MovingYPlatform:
                if self.player.rect.bottom <= platform.rect.top and self.player.rect.bottom >= platform.rect.top - 15:
                    mhits.append(platform)
                platform.update()
            if type(platform) is BrokenPlatform:
                if platform.update():
                    self.score += 10
                    platform.kill()
                    list.remove(self.platforms, platform)

        self.all_sprites.update()
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
                    self.score += 10
            for coin in self.cList:
                coin.rect.y += max(abs(self.player.vel.y), 5)
                if coin.rect.y >= HEIGHT:
                    coin.kill()
                    list.remove(self.cList, coin)

            for trap in self.tList:
                trap.rect.y += max(abs(self.player.vel.y), 5)
                if trap.rect.top >= HEIGHT:
                    trap.kill()
                    list.remove(self.tList, trap)

        # Spawn new platforms
        pListLen = len(self.platforms)
        pList = self.platforms

        while pListLen != 0 and self.player.rect.bottom - pList[pListLen - 1].rect.top < 240:
            if type(pList[pListLen - 1]) is not MovingYPlatform:
                pTopVal = pList[pListLen - 1].rect.top
                pBotVal = pList[pListLen - 1].rect.top
            else:
                pTopVal = pList[pListLen - 1].endY
                pBotVal = pList[pListLen - 1].startY
            if self.player.rect.bottom - pBotVal >= 240:
                break
            width = random.randrange(50, 100)
            trig = random.randrange(0, 100)
            mpPer = 6 + int(self.score / 37.037)
            bpPer = 4 + int(self.score / 25.555555555555555)
            if trig < mpPer:
                if random.randrange(0, 2) == 0 and self.score >= 1000:
                    startY = pTopVal - random.randrange(
                        50 + min(int(self.score / 10), 59), 110)
                    p = MovingYPlatform(self, random.randrange(0, WIDTH - width),
                                        startY, startY - random.randrange(100 + min(int(self.score / 10), 189), 300), random.randrange(2, 4))
                else:
                    cent = random.randrange(60, WIDTH - 90)
                    valWeight = random.randrange(60, 195)

                    startX = cent - valWeight
                    endX = cent + valWeight
                    if startX < 0:
                        startX = 0
                    if endX > WIDTH - 30:
                        endX = WIDTH - 30
                    p = MovingPlatform(self, startX, endX,
                                       pTopVal - random.randrange(50 + min(int(self.score / 10), 189), 240), random.randrange(3, 5 + int(self.score / 400)))
            elif trig < mpPer + bpPer:
                p = BrokenPlatform(self, random.randrange(0, WIDTH - width), pTopVal - random.randrange(
                    50 + min(int(self.score / 10), 189), 240))
            else:
                p = Platform(self, random.randrange(0, WIDTH - width), pTopVal - random.randrange(
                    50 + min(int(self.score / 10), 189), 240))
            self.platforms.append(p)
            self.all_sprites.add(p)
            pListLen = len(pList)
            pList = self.platforms
            # self.score += 10

        # #generate coin
        while len(self.cList) < 3:
            base = 0
            if len(self.cList) > 0:
                base = self.cList[len(self.cList) - 1].rect.top
            else:
                base = self.platforms[len(self.platforms) - 1].rect.top
            c = Coin(self, random.randrange(0, WIDTH - 30),
                     base - random.randrange(1000, 1600))
            self.all_sprites.add(c)
            self.cList.append(c)

        # # #check if player hits a coin
        cHits = pg.sprite.spritecollide(self.player, self.cList, False)
        if cHits:
            for cHit in cHits:
                self.score += 10
                cHit.kill()
                list.remove(self.cList, cHit)

        while len(self.tList) < 2 and self.score > 500:
            base = 0
            if len(self.tList) > 0:
                base = self.tList[len(self.tList) - 1].rect.top
            t = Trap(self, random.randrange(0, 2), base -
                     random.randrange(500, 1000), random.randrange(6, 13))
            self.all_sprites.add(t)
            self.tList.append(t)
            b = False

        tHits = pg.sprite.spritecollide(self.player, self.tList, False)
        if tHits:
            for tHit in tHits:
                if (type(tHit) is Trap):
                    if (tHit.check):
                        self.player.vel.x += tHit.speed
                    else:
                        self.player.vel.x -= tHit.speed

        # Die
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if type(sprite) is MovingYPlatform:
                    sprite.startY -= max(abs(self.player.vel.y), 5)
                    sprite.endY -= max(abs(self.player.vel.y), 5)
                if sprite.rect.bottom < 0:
                    sprite.kill()
                    if type(sprite) is Trap:
                        list.remove(self.tList, sprite)
                    elif type(sprite) is Coin:
                        list.remove(self.cList, sprite)
                    else:
                        list.remove(self.platforms, sprite)

        if len(self.platforms) <= 0:
            self.playing = False

        # check if player hits a platfrom
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            hits += mhits
            if hits:
                platform = hits[0]
                for hit in hits:
                    if hit.rect.bottom > platform.rect.bottom:
                        platform = hit
                if self.player.pos.y < platform.rect.centery:
                    self.player.pos.y = platform.rect.top + 0.1
                    self.player.vel.y = 0
                    self.player.jumping = False
                    if type(platform) is BrokenPlatform:
                        if platform.genTime == 2147483647:
                            platform.genTime = time.time()

    def events(self):
        # Game Loop - Events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            if event.type == pg.KEYDOWN:
                if event.key == KEY_JUMP:
                    if self.player.jump():
                        self.jump_sound.play()
            if event.type == pg.KEYUP:
                if event.key == KEY_JUMP:
                    self.player.jump_cut()

    def draw(self):
        if self.platforms.__len__() > 0:
            fet = self.platforms.pop()
        else:
            fet = Platform(self, 0, 0)
        self.platforms.append(fet)
        # Game Loop - Draw
        # self.screen.fill(BGCOLOR)

        self.screen.blit(draw_background, (0, 0))
        self.all_sprites.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)
        self.draw_text(str(self.score), 22, WHITE, WIDTH/2, 15)
        if DEBUG:
            self.draw_text("player y" +
                           str(self.player.rect.y), 22, WHITE, WIDTH/2, 40)
            self.draw_text("player x" +
                           str(self.player.rect.x), 22, WHITE, WIDTH/2, 40 + 25)
            self.draw_text("y of last appended platform" +
                           str(fet.rect.y), 22, WHITE, WIDTH/2, 65 + 25)
            self.draw_text("x of last appended platform" +
                           str(fet.rect.x), 22, WHITE, WIDTH/2, 90 + 25)
            self.draw_text("" + str(pg.sprite.spritecollide(self.player,
                           self.platforms, False)), 22, WHITE, WIDTH/2, 115 + 25)

        # *after* drawing everything, flip the display
        pg.display.flip()

    mn = 0

    def show_start_screen(self):
        self.mn = 0
        ui = []
        interactable = []
        ui.append(UIModule(WIDTH/2, HEIGHT/4, TITLE, WHITE, 48))
        ui.append(UIModule(WIDTH/2, HEIGHT/2,
                  "Arrows to move, Space to jump", WHITE, 22))
        ui.append(UIModule(WIDTH/2, HEIGHT * 3/4, "Start", WHITE, 22))
        ui.append(UIModule(WIDTH/2, HEIGHT * 3/4 + 25, "Options", WHITE, 22))
        ui.append(UIModule(WIDTH/2, HEIGHT * 3/4 + 25 + 25, "Quit", WHITE, 22))
        ui.append(UIModule(WIDTH/2, 15, "High Score : " +
                  str(self.highscore), WHITE, 22))

        interactable.append(
            UIModule(WIDTH/2, HEIGHT * 3/4, "Start", WHITE, 22))
        interactable.append(UIModule(WIDTH/2, HEIGHT * 3 /
                            4 + 25, "Options", WHITE, 22))
        interactable.append(UIModule(WIDTH/2, HEIGHT * 3 /
                            4 + 25 + 25, "Quit", WHITE, 22))
        # game splash/start screen
        while True:
            # self.screen.fill(BGCOLOR)
            self.screen.blit(draw_background, (0, 0))
            for m in ui:
                self.draw_text(m.text, m.fontSize, m.color, m.x, m.y)
            font = pg.font.SysFont('notosansmonocjkkrregular', 22)
            cur = font.render('>', True, WHITE)
            self.screen.blit(cur, (WIDTH/2 - 45, 5 + interactable[self.mn].y))
            pg.display.flip()
            for event in pg.event.get():
                # check for closing window
                if event.type == pg.QUIT:
                    self.running = False
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == KEY_UP and self.mn > 0:
                        self.mn -= 1
                    elif event.key == KEY_DOWN and self.mn < interactable.__len__() - 1:
                        self.mn += 1
                    elif event.key == KEY_ENTER:
                        if self.mn == 0:
                            print(KEY_LEFT)
                            return
                        elif self.mn == 1:
                            self.show_option_screen()
                        elif self.mn == 2:
                            self.running = False
                            pg.quit()
                            sys.exit()

    def keybind_screen(self):
        global KEY_LEFT
        global KEY_RIGHT
        global KEY_UP
        global KEY_DOWN
        global KEY_ENTER
        global KEY_JUMP
        self.mn = 0
        ui = []
        interactable = []
        dummy = 0   
        keyList = [dummy, KEY_LEFT, KEY_RIGHT,
                   KEY_UP, KEY_DOWN, KEY_ENTER, KEY_JUMP]
        ui.append(UIModule(WIDTH/2 - 140, HEIGHT *
                  1/6, "Exit Key Binding", WHITE, 22))
        ui.append(UIModule(WIDTH/2 - 150, HEIGHT * 1 /
                  6 + 30, "Left Key", WHITE, 22))
        ui.append(UIModule(WIDTH/2 - 150, HEIGHT *
                  1/6 + 60, "Right Key", WHITE, 22))
        ui.append(UIModule(WIDTH/2 - 150, HEIGHT *
                  1/6 + 90, "Up Key", WHITE, 22))
        ui.append(UIModule(WIDTH/2 - 150, HEIGHT *
                  1/6 + 120, "Down Key", WHITE, 22))
        ui.append(UIModule(WIDTH/2 - 150, HEIGHT *
                  1/6 + 150, "Enter Key", WHITE, 22))
        ui.append(UIModule(WIDTH/2 - 150, HEIGHT *
                  1/6 + 180, "Jump Key", WHITE, 22))

        interactable.append(
            UIModule(WIDTH/2 - 140, HEIGHT * 1/6, "Exit Key Binding", WHITE, 22))
        interactable.append(
            UIModule(WIDTH/2 - 150, HEIGHT * 1/6 + 30, "Left Key", WHITE, 22))
        interactable.append(
            UIModule(WIDTH/2 - 150, HEIGHT * 1/6 + 60, "Right Key", WHITE, 22))
        interactable.append(
            UIModule(WIDTH/2 - 150, HEIGHT * 1/6 + 90, "Up Key", WHITE, 22))
        interactable.append(UIModule(WIDTH/2 - 150, HEIGHT *
                                     1/6 + 120, "Down Key", WHITE, 22))
        interactable.append(UIModule(WIDTH/2 - 150, HEIGHT *
                                     1/6 + 150, "Enter Key", WHITE, 22))
        interactable.append(UIModule(WIDTH/2 - 150, HEIGHT *
                                     1/6 + 180, "Jump Key", WHITE, 22))

        while True:
            # self.screen.fill(BGCOLOR)
            self.screen.blit(draw_background, (0, 0))
            tVal = 0
            for m in ui:
                self.draw_text(m.text, m.fontSize, m.color, m.x, m.y)
                pg.draw.line(self.screen, WHITE, [
                    20, m.y], [460, m.y], 2)
                if tVal != 0:
                    self.draw_text(pg.key.name(
                        keyList[tVal]), 22, WHITE, m.x + 100, m.y)
                tVal += 1

            font = pg.font.SysFont('notosansmonocjkkrregular', 22)
            cur = font.render('>', True, WHITE)
            self.screen.blit(cur, (20, 5 + interactable[self.mn].y))
            pg.display.flip()
            for event in pg.event.get():
                # check for closing window
                if event.type == pg.QUIT:
                    self.running = False
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == KEY_UP and self.mn > 0:
                        self.mn -= 1
                    elif event.key == KEY_DOWN and self.mn < interactable.__len__() - 1:
                        self.mn += 1
                    elif event.key == KEY_ENTER:
                        if self.mn == 0:
                            return
                        else:
                            flag = True
                            while flag:
                                for event in pg.event.get():
                                    if event.type == pg.KEYDOWN:
                                        if event.key == pg.K_ESCAPE:
                                            flag = False
                                            break
                                        keyList[self.mn] = event.key
                                        flag = False
                            KEY_LEFT = keyList[1]
                            KEY_RIGHT = keyList[2]
                            KEY_UP = keyList[3]
                            KEY_DOWN = keyList[4]
                            KEY_ENTER = keyList[5]
                            KEY_JUMP = keyList[6]
                            Player.KeyChange(keyList)

    def show_option_screen(self):
        self.mn = 0
        ui = []
        interactable = []
        global BGMVOLUME
        global SFXVOLUME
        ui.append(UIModule(WIDTH/2 - 150, HEIGHT *
                  1/6, "Exit Settings", WHITE, 22))
        ui.append(UIModule(WIDTH/2 - 150, HEIGHT * 1 /
                  6 + 30, "Music Volume", WHITE, 22))
        ui.append(UIModule(WIDTH/2 - 150, HEIGHT *
                  1/6 + 90, "SFX Volume", WHITE, 22))
        ui.append(UIModule(WIDTH/2 - 150, HEIGHT *
                  1/6 + 150, "Key Binding", WHITE, 22))

        interactable.append(
            UIModule(WIDTH/2 - 150, HEIGHT * 1/6, "Exit Settings", WHITE, 22))
        interactable.append(
            UIModule(WIDTH/2 - 150, HEIGHT * 1/6 + 30, "Music Volume", WHITE, 22))
        interactable.append(
            UIModule(WIDTH/2 - 150, HEIGHT * 1/6 + 90, "SFX Volume", WHITE, 22))
        interactable.append(
            UIModule(WIDTH/2 - 150, HEIGHT * 1/6 + 150, "Key Binding", WHITE, 22))

        while True:
            # self.screen.fill(BGCOLOR)
            self.screen.blit(draw_background, (0, 0))
            for m in ui:
                self.draw_text(m.text, m.fontSize, m.color, m.x, m.y)
            pg.draw.line(self.screen, WHITE, [WIDTH/2 - 150, HEIGHT*1/6 + 70], [
                         WIDTH/2 - 150 + int(BGMVOLUME * 100) * 2, HEIGHT*1/6 + 70], 2)
            self.draw_text(str(int(BGMVOLUME * 100)), 22,
                           WHITE, 60, HEIGHT*1/6 + 60)
            pg.draw.line(self.screen, WHITE, [WIDTH/2 - 150, HEIGHT*1/6 + 130], [
                         WIDTH/2 - 150 + int(SFXVOLUME * 100) * 2, HEIGHT*1/6 + 130], 2)
            self.draw_text(str(int(SFXVOLUME * 100)), 22,
                           WHITE, 60, HEIGHT*1/6 + 120)

            pg.draw.line(self.screen, WHITE, [
                         20, HEIGHT*1/6], [460, HEIGHT*1/6], 2)
            pg.draw.line(self.screen, WHITE, [
                         20, HEIGHT*1/6 + 30], [460, HEIGHT*1/6 + 30], 2)
            pg.draw.line(self.screen, WHITE, [
                         20, HEIGHT*1/6 + 90], [460, HEIGHT*1/6 + 90], 2)
            pg.draw.line(self.screen, WHITE, [
                         20, HEIGHT*1/6 + 150], [460, HEIGHT*1/6 + 150], 2)

            font = pg.font.SysFont('notosansmonocjkkrregular', 22)
            cur = font.render('>', True, WHITE)
            self.screen.blit(cur, (20, 5 + interactable[self.mn].y))
            pg.display.flip()
            for event in pg.event.get():
                # check for closing window
                if event.type == pg.QUIT:
                    if self.playing:
                        self.playing = False
                    self.running = False
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == KEY_UP and self.mn > 0:
                        self.mn -= 1
                    elif event.key == KEY_DOWN and self.mn < interactable.__len__() - 1:
                        self.mn += 1
                    elif event.key == KEY_ENTER:
                        if self.mn == 0:
                            return
                        elif self.mn == 3:
                            self.keybind_screen()
                    elif event.key == KEY_LEFT:
                        if self.mn == 1 and BGMVOLUME >= 0.1:
                            BGMVOLUME -= 0.1
                        elif self.mn == 2 and SFXVOLUME >= 0.1:
                            SFXVOLUME -= 0.1
                    elif event.key == KEY_RIGHT:
                        if self.mn == 1 and BGMVOLUME < 1.0:
                            BGMVOLUME += 0.1
                        elif self.mn == 2 and SFXVOLUME < 1.0:
                            SFXVOLUME += 0.1

    def show_go_screen(self):
        # game over/continue
        if not self.running:
            return
        # self.screen.fill(BGCOLOR)
        self.screen.blit(end_background, (0, 0))
        self.gameover_sound.play()
        p = self.score
        if p == -10 or p < 0:
            p += 10

        # self.draw_text("GAME OVER", 48, WHITE, WIDTH/2, HEIGHT/4)
        self.draw_text("Score : " + str(p),
                       22, BLACK, WIDTH/2, HEIGHT/1/12)
        self.draw_text("Press ESC key to go to main menu",
                       22, BLACK, WIDTH/2, HEIGHT*10/12 - 30)
        self.draw_text("Press any key to play again",
                       22, BLACK, WIDTH/2, HEIGHT*10/12)

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
        global mainMenuFlag
        waiting = True
        while waiting:
            for event in pg.event.get():
                # check for closing window
                if event.type == pg.QUIT:
                    if self.playing:
                        self.playing = False
                    self.running = False
                    pg.quit()
                    sys.exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        mainMenuFlag = True
                    waiting = False

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
mainMenuFlag = False
while g.running:
    if mainMenuFlag :
        g.show_start_screen()
        mainMenuFlag = False
    g.new()
    g.show_go_screen()

pg.quit()
