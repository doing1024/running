import sys
import os
import pygame
import random
import thing


class Game:
    def __init__(self):
        # 初始化pygame
        pygame.init()
        pygame.mixer.init()
        # 设置常量
        self.fps = 60
        self.w = 1600
        self.h = 500
        self.stop = False
        self.jiover = 300
        self.jihight = lambda: random.randint(150, 300)
        self.screen = pygame.display.set_mode((self.w, self.h))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("./font.ttf", 50)
        # 加载图片
        self.loadimages()
        # 加载可碰撞物体
        self.player, self.background, self.ground = thing.thingGroup(
            self.images, self.w, self.h
        )
        # 加载技能
        self.fly, self.hide, self.big, self.bag = thing.jiGroup(
            self.images, self.fps, self.w, self.h
        )
        # 设置初始变量
        self.setvars()
        # 播放音乐
        self.loadmusic(1)

    def big_small(self, big):
        thing.big_small(self, big)

    def loadmusic(self, tp: int):
        """播放音乐，1=活，0=死"""
        thing.loadmusic(tp, pygame)

    def setvars(self):
        """初始化变量"""
        self.things = []
        self.ticktot = 0
        self.speed = 10
        self.nextspeed = 5
        self.down = 5
        self.up = 20
        self.random = 0.1
        self.lastguan = 0
        self.score = 0
        self.addspeed = 0
        self.addrandom = 0
        self.addup = 0
        self.dan = 0
        self.flystop = False
        [ji.reset() for ji in [self.fly, self.hide, self.big, self.bag]]

    def loadimages(self):
        """加载图片"""
        self.images = {}
        for i in os.listdir("./image"):
            self.images[i.split(".")[0]] = pygame.image.load(f"./image/{i}").convert()
            self.images[i.split(".")[0]].set_colorkey(([0, 0, 0]))

    def scale(self, image, w, h):
        """缩放图片"""
        return pygame.transform.scale(image, (w, h))

    def tick(self):
        """滴答一帧"""
        self.clock.tick(self.fps)
        self.ticktot += 1
        self.fly.tick()
        self.hide.tick()
        self.big.tick()
        self.bag.tick()
        if not self.stop:
            self.player.tick()
            self.background.tick()

    def tryover(self):
        """检查是否有应结束的技能"""
        if self.hide.needover():
            self.hide.over()
        if self.fly.needover():
            self.fly.over()
            self.addup = 0
        if self.big.needover():
            self.big.over()
            self.big_small(0.5)
            self.player.rect.x2 = self.player.x1 + self.player.rect.w
            self.player.rect.y2 = self.player.y1 + self.player.rect.h
            self.player.updateRectVars()
        if self.flystop:
            if self.addup > 0:
                self.addup -= 1
            else:
                self.flystop = False

    def show(self):
        """显示内容"""
        self.screen.blit(
            self.scale(self.background.image(), self.background.w, self.background.h),
            (self.background.x1, self.background.y1),
        )
        self.screen.blit(
            self.scale(self.ground.image(), self.ground.w, self.ground.h),
            (self.ground.x1, self.ground.y1),
        )
        if self.stop:
            self.screen.blit(
                self.font.render("Game Stop,Press P to continue", True, (255, 85, 85)),
                (500, 200),
            )
        if (self.hide.isbeing and self.ticktot % 2 == 0) or not self.hide.isbeing:
            self.screen.blit(
                self.scale(self.player.image(), self.player.w, self.player.h),
                (self.player.x1, self.player.y1),
            )
        showtext = f"Score: {self.score}\n"
        if self.fly.isbeing:
            showtext += f"飞天:{self.fly.sheng()}\n"
        if self.hide.isbeing:
            showtext += f"隐身:{self.hide.sheng()}\n"
        if self.big.isbeing:
            showtext += f"变大:{self.big.sheng()}\n"
        if self.dan:
            showtext += f"炸弹:{self.dan}"
        render = self.font.render(
                showtext,
                True,
                (255, 85, 85),
            )
        self.screen.blit(
            render,
            (self.ground.x2 - self.ground.w / 2 - render.get_width() / 2, self.ground.y2),
        )

    def makethings(self):
        if (
            self.ticktot % 20 == 0
            and random.random() < self.random + self.addrandom
        ):
            self.lastguan = self.ticktot
            height = random.randint(50, 150)
            self.things.append(
                thing.Thing(
                    "guan",
                    self.images,
                    ["guan"],
                    1,
                    self.w,
                    self.h - height - 125,
                    w=50,
                    h=height,
                )
            )
        for x in self.things:
            if x.tp != "guan":
                return
        if self.fly.canmake(self.score):
            self.things.append(self.fly.make())
        if self.hide.canmake(self.score):
            self.things.append(self.hide.make())
        if self.big.canmake(self.score):
            self.things.append(self.big.make())
        if self.bag.canmake(self.score):
            self.things.append(self.bag.make())

    def setthings(self):
        for i in range(len(self.things)):
            try:
                if (
                    self.fly.needpop(self.things[i])
                    or self.hide.needpop(self.things[i])
                    or self.big.needpop(self.things[i])
                    or self.bag.needpop(self.things[i])
                    or self.things[i].ndp
                ):
                    self.things.pop(i)
                    continue

                if not self.stop:
                    if self.things[i].tp != "dan":
                        self.things[i].move(-self.speed - self.addspeed, 0)
                    else:
                        y = 10
                        if self.things[i].y2 > self.ground.y1:
                            y = 0
                        self.things[i].move(10,y)
                    self.screen.blit(
                        self.scale(
                            self.things[i].image(), self.things[i].w, self.things[i].h
                        ),
                        (self.things[i].x1, self.things[i].y1),
                    )
                if self.things[i].tp == "dan":
                    t = self.things[i].peng(
                        self.things, True
                    )
                    if t != False:
                        self.things[t - 1].ndp = True
                        self.things.pop(i)
                        self.score += 1
                        continue
                if self.player.peng(self.things[i]):
                    if self.things[i].tp == "bag":
                        self.things.pop(i)
                        self.dan += 1
                        continue
                    elif self.things[i].tp == "guan":
                        if self.big.isbeing:
                            self.things.pop(i)
                            self.score += 2
                            continue
                        elif not self.hide.isbeing:
                            self.stop = True
                            self.loadmusic(1)
                            break
                    elif self.things[i].tp == "fly":
                        self.addup = 100
                        self.down = 0
                        self.fly.being()
                        self.things.pop(i)
                        continue
                    elif self.things[i].tp == "hide":
                        self.hide.being()
                        self.things.pop(i)
                        continue
                    elif self.things[i].tp == "big":
                        if not self.big.isbeing:
                            self.big.being()
                            self.big_small(2)
                            self.player.updateRectVars()
                        self.things.pop(i)
                        continue
                if self.things[i].x2 < 0:
                    self.things.pop(i)
                    i -= 1
                    self.score += 1
            except IndexError as e:
                pass

    def checkEvent(self):
        for event in pygame.event.get():
            if event == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_p:
                    if self.stop == False:
                        self.stop = True
                        self.loadmusic(0)
                    else:
                        self.stop = False
                        self.loadmusic(1)
                        self.setvars()
                elif event.key == pygame.K_r:
                    self.stop = False
                    self.loadmusic(1)
                elif event.key == pygame.K_6:
                    self.score += 10
                elif event.key == pygame.K_SPACE and self.dan:
                    self.dan -= 1
                    self.things.append(
                        thing.Thing(
                            "dan",
                            self.images,
                            ["bag"],
                            1,
                            self.player.x1,
                            self.player.y1,
                            self.player.x2,
                            self.player.y2,
                        )
                    )
        keys = pygame.key.get_pressed()
        if (
            keys[pygame.K_UP] or keys[pygame.K_w] or self.fly.isbeing
        ) and self.player.y1 > 0:
            self.player.move(0, -min(self.player.y1, self.up + self.addup))
            if self.ticktot % 10 == 0:
                self.up -= 1
            else:
                self.up = 20
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.addspeed += 0.1
            self.addrandom += 0.005
        else:
            if not self.fly.isbeing:
                self.addspeed = max(self.addspeed - 0.5, 0)
            self.addrandom = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.addspeed = 0
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.down += 1.5

    def movedown(self):
        # 掉落
        if self.player.y2 < self.ground.y1:
            self.player.move(0, self.down)
            if self.ticktot % 10 == 0:
                self.down = min(self.down + 1.5, 21)
                self.up = 20
        else:
            self.down = 5

    def addlevel(self):
        # 增加难度
        if self.ticktot % 100 == 0:
            self.random += 0.01
        if self.ticktot / self.fps > self.nextspeed and not self.stop:
            self.speed += 1
            self.nextspeed *= 2

    def flip(self):
        pygame.display.flip()
